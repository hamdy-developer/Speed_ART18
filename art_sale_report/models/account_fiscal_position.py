# -*- coding: utf-8 -*-

from odoo import models

class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    def map_tax(self, taxes):        # Using `raise_if_not_found=False` to avoid errors if the data record is deleted.
        tax_free_fp = self.env.ref('art_sale_report.fiscal_position_tax_free', raise_if_not_found=False)
        if tax_free_fp and self.id == tax_free_fp.id:
            return self.env['account.tax'] # Return empty recordset for taxes
        return super(AccountFiscalPosition, self).map_tax(taxes)
