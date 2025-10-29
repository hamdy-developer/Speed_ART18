from odoo import fields, models, api

class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    change_pricelist = fields.Boolean(
        string='Change Pricelist',
        help="If checked, the pricelist specified below will be applied to the Sales Order when this payment term is selected."
    )
    pricelist_id = fields.Many2one(
        'product.pricelist',
        string='Pricelist',
        help="The pricelist to apply to the Sales Order when this payment term is selected.",
    )