# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SalesClientWizard(models.TransientModel):
    _name = 'sales.client.wizard'
    _description = 'Sales Client Report Wizard'

    date_from = fields.Date(string='Start Date', required=True, default=fields.Date.context_today)
    date_to = fields.Date(string='End Date', required=True, default=fields.Date.context_today)
    partner_ids = fields.Many2many('res.partner', string='Partners')
    account_type = fields.Selection([
        ('receivable', 'Receivable'),
        ('payable', 'Payable'),
    ], string='Account Type', required=True, default='receivable')

    def action_print_report(self):
        """
        Called by the 'Print' button in the wizard.
        Gathers the data and calls the report action.
        """
        self.ensure_one()
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'partner_ids': self.partner_ids.ids,
            'account_type': self.account_type,
            'partner_names': ', '.join(self.partner_ids.mapped('name')) if self.partner_ids else 'All Partners'
        }
        return self.env.ref('sales_client_report.action_report_sales_client').report_action(self, data=data)