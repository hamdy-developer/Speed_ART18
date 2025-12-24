# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    sales_employee_id = fields.Many2one(
        'hr.employee',
        string='Sales Employee',
        help='The employee responsible for sales to this customer'
    )
