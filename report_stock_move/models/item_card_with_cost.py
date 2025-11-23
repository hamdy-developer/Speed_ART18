# report_item_card_with_cost.py

# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class GeneralLedgerAccount(models.AbstractModel):
    _name = 'report.report_stock_move.report_item_card_with_cost'
    _inherit = 'report.report_xlsx.abstract'

    def _get_converted_qty(self, line):
        """ Helper to convert quantity from a move line to the product's standard UoM """
        return line.product_uom_id._compute_quantity(line.quantity, line.product_id.uom_id)

    def generate_xlsx_report(self, workbook, data, wizard):
        for obj in wizard:
            sheet = workbook.add_worksheet('Stock Card')
            # --- Column & Workbook Formats (No changes here) ---
            # ... (your existing format definitions)
            sheet.set_column('A:A', 18);
            sheet.set_column('B:B', 30);
            sheet.set_column('C:C', 30)
            sheet.set_column('D:D', 20);
            sheet.set_column('E:E', 20);
            sheet.set_column('F:F', 12)
            sheet.set_column('G:G', 12);
            sheet.set_column('H:H', 15);
            sheet.set_column('I:I', 12)
            sheet.set_column('J:J', 12);
            sheet.set_column('K:K', 15);
            sheet.set_column('L:L', 12)
            sheet.set_column('M:M', 15);
            sheet.set_column('N:N', 15);
            sheet.set_column('O:O', 25)

            title_format = workbook.add_format({'font_size': 16, 'align': 'center', 'bold': True})
            header_format = workbook.add_format(
                {'font_size': 12, 'align': 'center', 'bold': True, 'border': 1, 'bg_color': '#D3D3D3'})
            product_header_format = workbook.add_format(
                {'font_size': 13, 'align': 'center', 'bold': True, 'border': 1, 'bg_color': '#A9A9A9'})
            location_header_format = workbook.add_format(
                {'font_size': 12, 'align': 'center', 'bold': True, 'border': 1, 'bg_color': '#E0E0E0'})
            data_format = workbook.add_format({'font_size': 10, 'border': 1, 'valign': 'vcenter'})
            date_format = workbook.add_format(
                {'font_size': 10, 'border': 1, 'num_format': 'yyyy-mm-dd hh:mm:ss', 'valign': 'vcenter'})
            float_format = workbook.add_format(
                {'font_size': 10, 'border': 1, 'num_format': '#,##0.00', 'valign': 'vcenter'})
            bold_float_format = workbook.add_format(
                {'font_size': 10, 'bold': True, 'border': 1, 'num_format': '#,##0.00', 'valign': 'vcenter'})

            row = 0
            sheet.merge_range(row, 0, row, 14, 'Stock Card Report', title_format)
            row += 2
            sheet.write(row, 0, 'From:', header_format);
            sheet.write(row, 1, str(obj.date_from))
            sheet.write(row, 3, 'To:', header_format);
            sheet.write(row, 4, str(obj.date_to))
            row += 2

            for product in obj.product_ids:
                sheet.merge_range(row, 0, row, 14, f"{product.name} ({product.default_code or 'N/A'})",
                                  product_header_format)
                row += 1

                # If lots are selected, we only care about those lots for this product.
                # Otherwise, we don't filter by lot.
                product_lots = obj.lot_ids.filtered(lambda l: l.product_id.id == product.id)

                for location in obj.location_ids:
                    sheet.merge_range(row, 0, row, 14, location.display_name, location_header_format)
                    row += 1

                    headers = [
                        'Date', 'Lot/Serial', 'From', 'To', 'Reference',
                        'In', 'Unit Cost', 'Total In', 'Out', 'Unit Cost', 'Total Out',
                        'Balance Qty', 'Avg Cost', 'Total Value', 'Partner'
                    ]
                    # Adjust columns for new "Lot/Serial" column
                    sheet.set_column('B:B', 20)  # Lot Column
                    for col, header in enumerate(headers):
                        sheet.write(row, col, header, header_format)
                    row += 1

                    # --- Build the base domain for stock.move.line ---
                    base_domain = [
                        ('product_id', '=', product.id),
                        ('state', '=', 'done'),
                        '|', ('location_id', '=', location.id), ('location_dest_id', '=', location.id),
                    ]
                    if obj.lot_ids:  # If user selected ANY lots in the wizard
                        if product_lots:  # If any of the selected lots match the current product
                            base_domain.append(('lot_id', 'in', product_lots.ids))
                        else:  # If lots were selected but NONE for this product, skip this product/location block
                            continue

                    # --- 1. Calculate Opening Balance from stock.move.line ---
                    opening_domain = base_domain + [('move_id.date', '<', obj.date_from)]
                    opening_lines = self.env['stock.move.line'].search(opening_domain)

                    opening_qty, opening_value = 0.0, 0.0
                    for line in opening_lines:
                        qty = self._get_converted_qty(line)
                        move = line.move_id
                        svl = self.env['stock.valuation.layer'].search([('stock_move_id', '=', move.id)], limit=1)
                        if not svl and move.move_dest_ids:
                            svl = self.env['stock.valuation.layer'].search(
                                [('stock_move_id', 'in', move.move_dest_ids.ids)], limit=1)

                        move_value = svl.value if svl else 0.0

                        if line.location_dest_id.id == location.id:  # IN
                            opening_qty += qty
                            opening_value += move_value
                        elif line.location_id.id == location.id:  # OUT
                            opening_qty -= qty
                            opening_value += move_value

                    sheet.merge_range(row, 0, row, 10, 'Opening Balance', header_format)
                    sheet.write_number(row, 11, opening_qty, bold_float_format)
                    opening_avg_cost = (opening_value / opening_qty) if opening_qty != 0 else 0.0
                    sheet.write_number(row, 12, opening_avg_cost, bold_float_format)
                    sheet.write_number(row, 13, opening_value, bold_float_format)
                    sheet.write_string(row, 14, '', data_format)
                    row += 1

                    running_qty, running_value = opening_qty, opening_value

                    # --- 2. Process Moves within the Date Range from stock.move.line ---
                    period_domain = base_domain + [('move_id.date', '>=', obj.date_from),
                                                   ('move_id.date', '<=', obj.date_to)]
                    period_lines = self.env['stock.move.line'].search(period_domain, order='date asc, id asc')

                    for line in period_lines:
                        qty = self._get_converted_qty(line)
                        move = line.move_id
                        svl = self.env['stock.valuation.layer'].search([('stock_move_id', '=', move.id)], limit=1)
                        if not svl and move.location_id.id == location.id and move.move_dest_ids:
                            svl = self.env['stock.valuation.layer'].search(
                                [('stock_move_id', 'in', move.move_dest_ids.ids)], limit=1)

                        move_value, unit_cost = 0.0, 0.0
                        if svl:
                            move_value = svl.value
                            if svl.quantity != 0:
                                unit_cost = abs(svl.value / svl.quantity)

                        in_qty, out_qty, in_value, out_value, in_unit_cost, out_unit_cost = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

                        if line.location_dest_id.id == location.id:  # IN move
                            in_qty, in_unit_cost, in_value = qty, unit_cost, move_value
                            running_qty += qty
                            running_value += move_value
                        elif line.location_id.id == location.id:  # OUT move
                            out_qty, out_unit_cost, out_value = qty, unit_cost, abs(move_value)
                            running_qty -= qty
                            running_value += move_value

                        # Write data row, note the column shift for Lot/Serial
                        sheet.write(row, 0, move.date, date_format)
                        sheet.write_string(row, 1, line.lot_id.name or '', data_format)  # NEW: Lot Name
                        sheet.write_string(row, 2, line.location_id.display_name, data_format)
                        sheet.write_string(row, 3, line.location_dest_id.display_name, data_format)
                        sheet.write_string(row, 4, move.reference or '', data_format)
                        # All subsequent columns are shifted by 1
                        sheet.write_number(row, 5, in_qty, float_format)
                        sheet.write_number(row, 6, in_unit_cost, float_format)
                        sheet.write_number(row, 7, in_value, float_format)
                        sheet.write_number(row, 8, out_qty, float_format)
                        sheet.write_number(row, 9, out_unit_cost, float_format)
                        sheet.write_number(row, 10, out_value, float_format)

                        sheet.write_number(row, 11, running_qty, bold_float_format)
                        running_avg_cost = (running_value / running_qty) if running_qty != 0 else 0.0
                        sheet.write_number(row, 12, running_avg_cost, bold_float_format)
                        sheet.write_number(row, 13, running_value, bold_float_format)
                        sheet.write_string(row, 14, move.picking_id.partner_id.name or '', data_format)
                        row += 1

                    row += 2
                row += 1