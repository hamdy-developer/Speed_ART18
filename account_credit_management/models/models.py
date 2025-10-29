from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    credit_limit = fields.Float(string='Credit Limit')

class AccountMove(models.Model):
    _inherit = 'account.move'

    eta_partner_id = fields.Many2one('res.partner', string='ETA Partner')

    def action_post(self):
        for move in self:
            if move.move_type == 'out_invoice' and move.partner_id.credit_limit > 0:
                # The 'credit' field on res.partner is a computed field that calculates the total credit of the partner.
                # It is the standard way to get the partner's credit in Odoo.
                allowed_credit = move.partner_id.credit_limit - move.partner_id.credit
                if move.amount_total > allowed_credit:
                    raise UserError(_('Cannot validate invoice. Credit limit exceeded for partner: %s') % move.partner_id.name)
        return super(AccountMove, self).action_post()

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        for order in self:
            if order.partner_id.credit_limit > 0:

                allowed_credit = order.partner_id.credit_limit - order.partner_id.credit
                if order.amount_total > allowed_credit:
                    raise UserError(_('Cannot confirm sale order. Credit limit exceeded for partner: %s') % order.partner_id.name)
        return super(SaleOrder, self).action_confirm()