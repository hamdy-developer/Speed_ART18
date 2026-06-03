# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models
from odoo.tools import SQL


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    sales_employee_id = fields.Many2one('hr.employee', string='Sales Employee', readonly=True)

    def _select(self) -> SQL:
        return SQL("%s, move.sales_employee_id AS sales_employee_id", super()._select())
