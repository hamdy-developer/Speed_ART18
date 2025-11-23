# -*- coding: utf-8 -*-
from datetime import date

from odoo import _, api, fields, models


class GeneralLedgerAccount(models.AbstractModel):
    _name = 'report.report_stock_move.report_location'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        for obj in partners:
            sheet = workbook.add_worksheet('Stock Card')
            sheet.set_column('A:A', 25)
            sheet.set_column('B:B', 45)
            sheet.set_column('C:C', 45)
            sheet.set_column('D:D', 30)
            sheet.set_column('E:E', 13)
            sheet.set_column('F:F', 13)
            sheet.set_column('G:G', 13)
            sheet.set_column('H:H', 13)
            sheet.set_column('J:J', 13)
            format2 = workbook.add_format(
                {'font_size': 13, 'align': 'center', 'bold': True,
                 'border': 1, 'bg_color': '#33FCFF', 'num_format': '0.00'})
            format3 = workbook.add_format(
                {'align': 'center', 'bold': True, 'bg_color': '#6495ED', 'color': 'white', 'border': 5})
            format4 = workbook.add_format(
                {'align': 'center', 'bold': True, 'bg_color': '#424949', 'color': 'white', 'border': 5})
            format5 = workbook.add_format(
                {'align': 'center', 'bold': True, 'bg_color': '#581845', 'color': '#DE3163', 'border': 5})
            format6 = workbook.add_format(
                {'align': 'center', 'bold': True, 'bg_color': '#DFFF00', 'color': 'black', 'border': 5})
            format7 = workbook.add_format(
                {'align': 'center', 'bold': True, 'bg_color': '#40E0D0', 'color': '#DE3163', 'border': 5,
                 'font_size': 15})
            format9 = workbook.add_format(
                {'align': 'center', 'bold': True, 'bg_color': '#FFC300', 'color': '#4A235A', 'border': 5,
                 'font_size': 13})
            format10 = workbook.add_format(
                {'align': 'center', 'bold': True, 'bg_color': '#5FEC14', 'color': '#DE3163', 'border': 5})
            row = 0
            sheet.write(row, 2, 'Stock card', format7)
            row += 1
            sheet.write(row, 1, 'FROM : ' + str(obj.date_from), format6)
            sheet.write(row, 3, 'TO : ' + str(obj.date_to), format6)
            row += 1
            if obj.location_ids and obj.product_ids:
                level = 1
                level2 = 2
                for product in obj.product_ids:
                    row += 1
                    sheet.set_row(row, None, None, {'level': level, 'hidden': False})
                    sheet.merge_range(row, 1, row, 3, product.name, format5)
                    sheet.write(row, 0, product.barcode, format10)
                    row += 1
                    for location in obj.location_ids:
                        stocks_from = self.env['stock.move'].sudo().search([('product_id', '=', product.id),
                                                                            ('location_id', '=', location.id),
                                                                            ('state', '=', 'done'),
                                                                            ('date', '>=', obj.date_from),
                                                                            ('date', '<=', obj.date_to), ]).mapped(
                            'id')
                        stocks_to = self.env['stock.move'].sudo().search([('product_id', '=', product.id),
                                                                          ('location_dest_id', '=', location.id),
                                                                          ('state', '=', 'done'),
                                                                          ('date', '>=', obj.date_from),
                                                                          ('date', '<=', obj.date_to), ]).mapped('id')
                        stocks_to.extend(stocks_from)
                        stocks = self.env['stock.move'].sudo().search([
                            ('id', 'in', stocks_to),
                        ], order="date ASC")
                        balance_from = self.env['stock.move'].sudo().search([('product_id', '=', product.id),
                                                                             ('location_id', '=', location.id),
                                                                             ('state', '=', 'done'),
                                                                             ('date', '>=', date(2022, 1, 1)),
                                                                             ('date', '<', obj.date_from), ])
                        total_balance_in = 0
                        for balance_in in balance_from:
                            if balance_in.product_uom.uom_type == 'smaller':
                                if balance_in.product_uom.factor:
                                    total_balance_in += balance_in.product_uom_qty / balance_in.product_uom.factor
                            elif balance_in.product_uom.uom_type == 'bigger':
                                total_balance_in += balance_in.product_uom_qty * balance_in.product_uom.factor_inv
                            else:
                                total_balance_in += balance_in.product_uom_qty
                        balance_to = self.env['stock.move'].sudo().search([('product_id', '=', product.id),
                                                                           ('location_dest_id', '=', location.id),
                                                                           ('state', '=', 'done'),
                                                                           ('date', '>=', date(2022, 1, 1)),
                                                                           ('date', '<', obj.date_from), ])
                        total_balance_to = 0
                        for balance_to_to in balance_to:
                            if balance_to_to.product_uom.uom_type == 'smaller':
                                if balance_to_to.product_uom.factor:
                                    total_balance_to += balance_to_to.product_uom_qty / balance_to_to.product_uom.factor
                            elif balance_to_to.product_uom.uom_type == 'bigger':
                                total_balance_to += balance_to_to.product_uom_qty * balance_to_to.product_uom.factor_inv
                            else:
                                total_balance_to += balance_to_to.product_uom_qty
                        balance = total_balance_to - total_balance_in
                        sheet.set_row(row, None, None, {'level': level, 'hidden': False})
                        sheet.write(row, 2, location.display_name, format9)
                        row += 1
                        sheet.set_row(row, None, None, {'level': level, 'hidden': False})
                        sheet.set_row(row, None, None, {'level': level2, 'hidden': False})
                        sheet.write(row, 0, 'Date', format3)
                        sheet.write(row, 1, 'From', format3)
                        sheet.write(row, 2, 'To', format3)
                        sheet.write(row, 3, 'Reference', format3)
                        sheet.write(row, 4, 'In', format3)
                        sheet.write(row, 5, 'Out', format3)
                        sheet.write(row, 6, 'Balance', format3)
                        row += 1
                        sheet.set_row(row, None, None, {'level': level, 'hidden': False})
                        sheet.set_row(row, None, None, {'level': level2, 'hidden': False})
                        sheet.merge_range(row, 0, row, 5, "Balance", format4)
                        sheet.write(row, 6, balance, format2)
                        row += 1
                        if stocks:
                            for stock in stocks:
                                if location.id == stock.location_id.id:
                                    sheet.set_row(row, None, None, {'level': level, 'hidden': False})
                                    sheet.set_row(row, None, None, {'level': level2, 'hidden': False})
                                    sheet.write(row, 0, str(stock.date), format2)
                                    sheet.write(row, 1, stock.location_id.display_name, format2)
                                    sheet.write(row, 2, stock.location_dest_id.display_name, format2)
                                    sheet.write(row, 3, stock.reference, format2)
                                    sheet.write(row, 4, 0, format2)
                                    if stock.product_uom.uom_type == 'smaller':
                                        sheet.write(row, 5, stock.product_uom_qty / stock.product_uom.factor, format2)
                                        balance += 0 - (stock.product_uom_qty / stock.product_uom.factor)
                                        sheet.write(row, 6, balance, format2)
                                    elif stock.product_uom.uom_type == 'bigger':
                                        sheet.write(row, 5, stock.product_uom_qty * stock.product_uom.factor_inv,
                                                    format2)
                                        balance += 0 - (stock.product_uom_qty * stock.product_uom.factor_inv)
                                        sheet.write(row, 6, balance, format2)
                                    else:
                                        sheet.write(row, 5, stock.product_uom_qty, format2)
                                        balance += 0 - stock.product_uom_qty
                                        sheet.write(row, 6, balance, format2)
                                elif location.id == stock.location_dest_id.id:
                                    sheet.set_row(row, None, None, {'level': level, 'hidden': False})
                                    sheet.set_row(row, None, None, {'level': level2, 'hidden': False})
                                    sheet.write(row, 0, str(stock.date), format2)
                                    sheet.write(row, 1, stock.location_id.display_name, format2)
                                    sheet.write(row, 2, stock.location_dest_id.display_name, format2)
                                    sheet.write(row, 3, stock.reference, format2)
                                    if stock.product_uom.uom_type == 'smaller':
                                        sheet.write(row, 4, stock.product_uom_qty / stock.product_uom.factor, format2)
                                        sheet.write(row, 5, 0, format2)
                                        balance += (stock.product_uom_qty / stock.product_uom.factor) - 0
                                        sheet.write(row, 6, balance, format2)
                                    elif stock.product_uom.uom_type == 'bigger':
                                        sheet.write(row, 4, stock.product_uom_qty * stock.product_uom.factor_inv,
                                                    format2)
                                        sheet.write(row, 5, 0, format2)
                                        balance += (stock.product_uom_qty * stock.product_uom.factor_inv) - 0
                                        sheet.write(row, 6, balance, format2)
                                    else:
                                        sheet.write(row, 4, stock.product_uom_qty, format2)
                                        sheet.write(row, 5, 0, format2)
                                        balance += stock.product_uom_qty - 0
                                        sheet.write(row, 6, balance, format2)
                                row += 1
                                sheet.set_row(row, None, None, {'level': level, 'hidden': False})
                    row += 1
