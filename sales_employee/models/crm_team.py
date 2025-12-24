# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    sales_employee_ids = fields.Many2many(
        'hr.employee',
        'crm_team_sales_employee_rel',
        'team_id',
        'employee_id',
        string='Sales Employees',
        help='Employees assigned to this sales team'
    )
