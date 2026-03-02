from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    credit_limit = fields.Float(string='Credit Limit')

class AccountMove(models.Model):
    _inherit = 'account.move'

    eta_partner_id = fields.Many2one('res.partner', string='ETA Partner')

    price_total_no_discount = fields.Monetary(
        compute="_compute_discount_amounts",
        string="Total Without Discount",
        currency_field="currency_id",
    )
    discount_total = fields.Monetary(
        compute="_compute_discount_amounts",
        string="Discount Total",
        currency_field="currency_id",
    )

    @api.depends('invoice_line_ids.price_total_no_discount', 'invoice_line_ids.discount_total')
    def _compute_discount_amounts(self):
        for move in self:
            move.price_total_no_discount = sum(move.invoice_line_ids.mapped('price_total_no_discount'))
            move.discount_total = sum(move.invoice_line_ids.mapped('discount_total'))

    def action_post(self):
        for move in self:
            if move.move_type == 'out_invoice' and move.partner_id.credit_limit > 0:
                # The 'credit' field on res.partner is a computed field that calculates the total credit of the partner.
                # It is the standard way to get the partner's credit in Odoo.
                allowed_credit = move.partner_id.credit_limit - move.partner_id.credit
                if move.amount_total > allowed_credit:
                    raise UserError(_('Cannot validate invoice. Credit limit exceeded for partner: %s') % move.partner_id.name)
        return super(AccountMove, self).action_post()


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    price_total_no_discount = fields.Monetary(
        compute="_compute_discount_amounts",
        string="Total Without Discount",
        store=True,
    )
    discount_total = fields.Monetary(
        compute="_compute_discount_amounts",
        string="Discount Total",
        store=True,
    )

    @api.depends('quantity', 'discount', 'price_unit', 'tax_ids')
    def _compute_discount_amounts(self):
        for line in self:
            line.price_total_no_discount = 0.0
            line.discount_total = 0.0
            if not line.move_id.is_invoice(include_receipts=True):
                continue

            price = line.price_unit
            quantity = line.quantity or 0.0
            
            # Compute taxes without discount
            taxes = line.tax_ids.compute_all(
                price,
                line.move_id.currency_id,
                quantity,
                product=line.product_id,
                partner=line.move_id.partner_id,
            )

            line.price_total_no_discount = taxes["total_included"]
            line.discount_total = line.price_total_no_discount - line.price_total


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        for order in self:
            if order.partner_id.credit_limit > 0:

                allowed_credit = order.partner_id.credit_limit - order.partner_id.credit
                if order.amount_total > allowed_credit:
                    raise UserError(_('Cannot confirm sale order. Credit limit exceeded for partner: %s') % order.partner_id.name)
        return super(SaleOrder, self).action_confirm()