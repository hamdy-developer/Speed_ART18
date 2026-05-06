from odoo import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta

class CustomerDebtReportWizard(models.TransientModel):
    _name = 'customer.debt.report.wizard'
    _description = 'Customer Debt Report Wizard'

    date_from = fields.Date(string='Start Month', default=fields.Date.today(), required=True)
    partner_ids = fields.Many2many('res.partner', string='Partners', domain="[('customer_rank', '>', 0)]")
    number_of_months = fields.Integer(string='Number of Months', default=10, required=True)

    def action_print_xlsx(self):
        self.ensure_one()
        data = {
            'date_from': self.date_from,
            'partner_ids': self.partner_ids.ids,
            'number_of_months': self.number_of_months,
        }
        return self.env.ref('customer_debt_monthly_report.customer_debt_report_xlsx_action').report_action(self, data=data)
