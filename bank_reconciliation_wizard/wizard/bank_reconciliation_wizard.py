# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BankReconciliationWizard(models.TransientModel):
    _name = 'bank.reconciliation.wizard'
    _description = 'Bank Reconciliation Report Wizard'

    date_from = fields.Date(
        string='Start Date',
        required=True,
        default=fields.Date.context_today,
        help='Start date for the report'
    )
    date_to = fields.Date(
        string='End Date',
        required=True,
        default=fields.Date.context_today,
        help='End date for the report'
    )
    partner_ids = fields.Many2many(
        'res.partner',
        string='Partners',
        help='Filter by specific partners (optional)'
    )
    journal_ids = fields.Many2many(
        'account.journal',
        string='Bank Journals',
        domain="[('type', '=', 'bank')]",
        help='Filter by specific bank journals (optional)'
    )

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        """Ensure that date_from is before or equal to date_to"""
        for wizard in self:
            if wizard.date_from and wizard.date_to:
                if wizard.date_from > wizard.date_to:
                    raise UserError(_('Start Date must be before or equal to End Date.'))

    def action_print_report(self):
        """Open Bank Statement Lines with applied filters"""
        self.ensure_one()
        
        # Build domain for filtering
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
        ]
        
        # Add journal filter if journals are selected
        if self.journal_ids:
            domain.append(('journal_id', 'in', self.journal_ids.ids))
        
        # Add partner filter if partners are selected
        if self.partner_ids:
            domain.append(('partner_id', 'in', self.partner_ids.ids))
        
        # Return action to open bank statement lines
        return {
            'name': _('Bank Statement Lines'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.bank.statement.line',
            'view_mode': 'list,form',
            'domain': domain,
            'context': {
                'default_date': self.date_to,
                'search_default_date_from': self.date_from,
                'search_default_date_to': self.date_to,
            },
        }
