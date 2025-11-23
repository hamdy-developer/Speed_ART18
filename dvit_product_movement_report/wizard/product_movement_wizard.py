from odoo import models, fields, _
import io
import base64
from collections import defaultdict
from datetime import datetime
from dateutil.relativedelta import relativedelta
import xlsxwriter



class ProductMovementWizard(models.TransientModel):
    _name = "product.movement.wizard"
    _description = "Product Movement Wizard"

    date_from = fields.Date(string="Date From", required=True)
    date_to = fields.Date(string="Date To", required=True)
    location_ids = fields.Many2many("stock.location", string="Locations", required=True)

    def action_view_report(self):
        # Compute and populate stock movements
        if self.date_from > self.date_to:
            raise ValueError(_("Date From cannot be later than Date To"))

        self.env["stock.movement.report"].compute_stock_movements(self.date_from, self.date_to, self.location_ids.ids)
        print('ddddddddddddd')
        print('ddddddddddddd')
        print('ddddddddddddd')
        print('ddddddddddddd')
        # Filter the data for the tree view
        domain = [
            ("location_id", "in", self.location_ids.ids),
            ("date", ">=", self.date_from),
            ("date", "<=", self.date_to),
        ]
        records = self.env["stock.movement.report"].search(domain)
        print('records',records)

        # Reference the action and add group_by
        action = self.env.ref("dvit_product_movement_report.action_stock_movement_tree_view").read()[0]
        action["domain"] = [("id", "in", records.ids)]
        action["context"] = {"date_from": self.date_from,
                             "date_to": self.date_to,
                             "group_by": ["location_id", "date:month"]}
        return action

    def action_export_excel(self):
        date_from = self.date_from
        date_to = self.date_to
        location_ids = self.location_ids.ids

        # Generate months between date_from and date_to
        months = []
        current_date = date_from
        while current_date <= date_to:
            months.append(current_date.strftime('%Y-%m'))
            current_date += relativedelta(months=1)

        # Fetch stock moves
        incoming_moves = self.env["stock.move.line"].search([
            ("date", ">=", date_from),
            ("date", "<=", date_to),
            ("location_dest_id", "in", location_ids),
            ("state", "=", "done"),
        ])

        outgoing_moves = self.env["stock.move.line"].search([
            ("date", ">=", date_from),
            ("date", "<=", date_to),
            ("location_id", "in", location_ids),
            ("state", "=", "done"),
        ])

        # Initialize data structure
        grouped_data = defaultdict(
            lambda: defaultdict(lambda: {month: {'in_qty': 0, 'out_qty': 0, 'balance': 0} for month in months})
        )

        # Process stock moves
        for move in incoming_moves:
            month_key = move.date.strftime('%Y-%m')
            location_key = move.location_dest_id.complete_name
            product_key = move.product_id.display_name

            grouped_data[location_key][product_key][month_key]['in_qty'] += move.qty_done

        for move in outgoing_moves:
            month_key = move.date.strftime('%Y-%m')
            location_key = move.location_id.complete_name
            product_key = move.product_id.display_name

            grouped_data[location_key][product_key][month_key]['out_qty'] += move.qty_done

        # Calculate totals and balances
        totals = {}
        for location_name, products in grouped_data.items():
            totals[location_name] = {month: {'in_qty': 0, 'out_qty': 0, 'balance': 0} for month in months}
            for product_name, month_data in products.items():
                previous_balance = 0
                for month in months:
                    data = month_data[month]
                    # Include previous balance for the product
                    # data['in_qty'] += previous_balance
                    data['balance'] = round(previous_balance+data['in_qty'] - data['out_qty'], 2)
                    previous_balance = data['balance']
                    # Add to location totals
                    totals[location_name][month]['in_qty'] += data['in_qty']
                    totals[location_name][month]['out_qty'] += data['out_qty']
                    totals[location_name][month]['balance'] += data['balance']

        # Create Excel file
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet("Stock Movement Report")

        # Define header
        worksheet.write(0, 0, "Location")
        worksheet.write(0, 1, "Product")
        col = 2
        for month in months:
            worksheet.merge_range(0, col, 0, col + 2, month, workbook.add_format({'align': 'center', 'bold': True}))
            worksheet.write(1, col, "In Qty")
            worksheet.write(1, col + 1, "Out Qty")
            worksheet.write(1, col + 2, "Balance")
            col += 3

        # Write data rows
        row = 2
        for location_name, products in grouped_data.items():
            # Write location name and totals on the same row
            worksheet.write(row, 0, location_name)
            col = 2
            for month in months:
                total_data = totals[location_name][month]
                worksheet.write(row, col, total_data['in_qty'])  # Write location total in_qty
                worksheet.write(row, col + 1, total_data['out_qty'])  # Write location total out_qty
                worksheet.write(row, col + 2, total_data['balance'])  # Write location total balance
                col += 3

            row += 1  # Move to the next row for products
            for product_name, month_data in products.items():
                worksheet.write(row, 1, product_name)  # Write product name
                col = 2
                for month in months:
                    data = month_data[month]
                    worksheet.write(row, col, data['in_qty'])
                    worksheet.write(row, col + 1, data['out_qty'])
                    worksheet.write(row, col + 2, data['balance'])
                    col += 3
                row += 1

        # Close the workbook
        workbook.close()

        # Encode file
        output.seek(0)
        file_data = base64.b64encode(output.read())
        output.close()

        # Create and return attachment
        attachment = self.env["ir.attachment"].create({
            "name": "Stock_Movement_Report.xlsx",
            "type": "binary",
            "datas": file_data,
            "res_model": self._name,
            "res_id": self.id,
            "mimetype": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        })

        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/{attachment.id}?download=true",
            "target": "self",
        }

    def action_export_pdf(self):
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'location_ids': self.location_ids.ids,
        }
        return self.env.ref("dvit_product_movement_report.product_movement_pdf_report").report_action(self, data=data)
