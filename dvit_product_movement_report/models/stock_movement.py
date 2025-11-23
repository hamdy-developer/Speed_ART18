from odoo import models, fields, api
from collections import defaultdict
from dateutil.relativedelta import relativedelta
from datetime import datetime


class StockMovementReport(models.AbstractModel):
    _name = 'report.dvit_product_movement_report.pdf_template'
    _description = 'Stock Movement Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_from = datetime.strptime(data.get('date_from'), '%Y-%m-%d')
        date_to = datetime.strptime(data.get('date_to'), '%Y-%m-%d')
        location_ids = data.get('location_ids')
        incoming_moves = self.env["stock.move.line"].search([
            ("date", ">=", date_from),
            ("date", "<=", date_to),
            ("location_dest_id", "in", location_ids),
            ("state", "=", "done"),
        ])

        outgoing_moves = self.env['stock.move.line'].search(
            [
                ('location_id', 'in', location_ids),
                ('state', '=', 'done'),
                ('date', '>=', date_from),
                ('date', '<=', date_to),
            ],
        )


        # Generate all months between date_from and date_to
        months = []
        current_date = date_from
        while current_date <= date_to:
            months.append(current_date.strftime('%Y-%m'))
            current_date += relativedelta(months=1)

        # Initialize data structure
        grouped_data = defaultdict(lambda: {month: {'in_qty': 0, 'out_qty': 0, 'balance': 0} for month in months})

        # Process stock moves
        for move in incoming_moves:
            month_key = move.date.strftime('%Y-%m')

            if month_key in grouped_data[move.location_dest_id.complete_name]:
                if move.location_dest_id.id in location_ids:
                    grouped_data[move.location_dest_id.complete_name][month_key]['in_qty'] += move.qty_done

        for move in outgoing_moves:
            month_key = move.date.strftime('%Y-%m')

            if month_key in grouped_data[move.location_id.complete_name]:
                if move.location_id.id in location_ids:
                    grouped_data[move.location_id.complete_name][month_key]['out_qty'] += move.qty_done

        # Adjust in_qty to include previous balances, calculate balance, and round
        for location_name, month_data in grouped_data.items():
            previous_balance = 0  # Initialize the previous balance as 0
            for month in months:  # Iterate over all months
                if month in month_data:
                    data = month_data[month]
                    # Update in_qty to include the previous balance
                    # data['in_qty'] += previous_balance
                    # Round in_qty to two decimal places
                    data['in_qty'] = round(data['in_qty'], 2)
                    # Calculate and round balance for the current month
                    data['balance'] = round(previous_balance+data['in_qty'] - data['out_qty'], 2)
                    # Round out_qty to two decimal places
                    data['out_qty'] = round(data['out_qty'], 2)
                    # Update previous_balance for the next month
                    previous_balance = data['balance']

        return {
            'data': data,
            'grouped_data': grouped_data,
            'months': months,
            'locations': [location.complete_name for location in self.env['stock.location'].browse(location_ids)],
        }


class StockMovementReportView(models.Model):
    _name = "stock.movement.report"
    _description = "Stock Movement Report"

    product_id = fields.Many2one("product.product", string="Product", readonly=True)
    location_id = fields.Many2one("stock.location", string="Location", readonly=True)
    date = fields.Date(string="Date", readonly=True)
    in_qty = fields.Float(string="In Quantity", readonly=True)
    out_qty = fields.Float(string="Out Quantity", readonly=True)
    balance = fields.Float(string="Balance", readonly=True)
    month = fields.Char(string="Month", compute="_compute_month", store=True)

    @api.depends('date')
    def _compute_month(self):
        for record in self:
            if record.date:
                record.month = record.date.strftime('%Y-%m')  # Format as 'YYYY-MM'

    @api.model
    def compute_stock_movements(self, date_from, date_to, location_ids):
        # Clear existing data (if required, e.g., for a fresh report each time)
        self.search([]).unlink()

        # Fetch incoming moves (to the specified locations within the date range)
        incoming_moves = self.env['stock.move.line'].search(
            [
                ('location_dest_id', 'in', location_ids),
                ('state', '=', 'done'),
                ('date', '>=', date_from),
                ('date', '<=', date_to),
            ],
        )

        # Fetch outgoing moves (from the specified locations within the date range)
        outgoing_moves = self.env['stock.move.line'].search(
            [
                ('location_id', 'in', location_ids),
                ('state', '=', 'done'),
                ('date', '>=', date_from),
                ('date', '<=', date_to),
            ],
        )

        # Initialize a dictionary to track balances
        balance_tracker = {}

        # Process incoming moves
        for move in incoming_moves:
            product_id = move.product_id
            location_id = move.location_dest_id
            in_qty = move.qty_done
            date = move.date.date()

            key = (product_id, location_id,date)
            if key not in balance_tracker:
                balance_tracker[key] = {'in_qty': 0, 'out_qty': 0, 'balance': 0}

            balance_tracker[key]['in_qty'] += in_qty
            balance_tracker[key]['balance'] += in_qty

        # Process outgoing moves
        for move in outgoing_moves:
            product_id = move.product_id
            location_id = move.location_id
            date =  move.date.date()
            out_qty = move.qty_done

            key = (product_id, location_id,date)
            if key not in balance_tracker:
                balance_tracker[key] = {'in_qty': 0, 'out_qty': 0, 'balance': 0}

            balance_tracker[key]['out_qty'] += out_qty
            balance_tracker[key]['balance'] -= out_qty

        # Create stock movement records
        for key, values in balance_tracker.items():
            product_id, location_id,date = key
            self.create({
                "product_id": product_id.id,
                "location_id": location_id.id,
                "in_qty": values['in_qty'],
                "out_qty": values['out_qty'],
                "balance": values['balance'],
                "date": date,

            })
