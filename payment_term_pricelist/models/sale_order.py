from odoo import fields, models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('payment_term_id')
    def _onchange_payment_term_id_pricelist(self):
        if self.payment_term_id and self.payment_term_id.change_pricelist and self.payment_term_id.pricelist_id:
            self.pricelist_id = self.payment_term_id.pricelist_id