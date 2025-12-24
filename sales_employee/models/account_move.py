# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    sales_employee_id = fields.Many2one(
        'hr.employee',
        string='Sales Employee',
        compute='_compute_sales_employee_id',
        store=True,
        readonly=True,
        help='Sales Employee from the related Sale Order'
    )

    @api.depends('invoice_line_ids.sale_line_ids.order_id.sales_employee_id')
    def _compute_sales_employee_id(self):
        for move in self:
            sale_orders = move.invoice_line_ids.sale_line_ids.order_id
            if sale_orders:
                # Get the first sales employee from linked sale orders
                move.sales_employee_id = sale_orders[0].sales_employee_id
            else:
                move.sales_employee_id = False
