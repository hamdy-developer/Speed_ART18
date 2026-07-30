from odoo import models, fields, api

class CustomerDebtBrandReportWizard(models.TransientModel):
    _name = 'customer.debt.brand.report.wizard'
    _description = 'Customer Debt Brand Report Wizard'

    date_from = fields.Date(string='Start Month', default=fields.Date.today(), required=True)
    report_by = fields.Selection([
        ('employee', 'Sales Employee'),
        ('brand', 'Brand')
    ], string='Report By', default='employee', required=True)
    employee_ids = fields.Many2many('hr.employee', string='Sales Employees')
    brand_ids = fields.Many2many('product.brand', string='Brands')
    number_of_months = fields.Integer(string='Number of Months', default=10, required=True)

    def action_print_xlsx(self):
        self.ensure_one()
        data = {
            'date_from': self.date_from,
            'report_by': self.report_by,
            'employee_ids': self.employee_ids.ids,
            'brand_ids': self.brand_ids.ids,
            'number_of_months': self.number_of_months,
        }
        return self.env.ref('customer_debt_monthly_report.customer_debt_brand_report_xlsx_action').report_action(self, data=data)
