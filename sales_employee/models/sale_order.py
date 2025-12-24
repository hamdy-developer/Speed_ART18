# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sales_employee_id = fields.Many2one(
        'hr.employee',
        string='Sales Employee',
        compute='_compute_sales_employee_id',
        store=True,
        readonly=False,
        precompute=True,
        help='Sales Employee fetched from the customer'
    )

    @api.depends('partner_id')
    def _compute_sales_employee_id(self):
        for order in self:
            if order.partner_id and not (order._origin.id and order.sales_employee_id):
                order.sales_employee_id = (
                    order.partner_id.sales_employee_id
                    or order.partner_id.commercial_partner_id.sales_employee_id
                )
