# -*- coding: utf-8 -*-

from odoo import models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def action_open_partner_ledger(self):
        """Open Partner Ledger report filtered by current partner"""
        self.ensure_one()
        
        # Use the standard account_reports action
        action = self.env["ir.actions.actions"]._for_xml_id("account_reports.action_account_report_partner_ledger")
        action['params'] = {
            'options': {
                'partner_ids': [self.id],
                'unfold_all': True,
            },
            'ignore_session': True,
        }
        return action