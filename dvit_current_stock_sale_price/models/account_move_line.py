# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    cost_product = fields.Float(
        related='product_id.standard_price', store=True)
    product_categ_id = fields.Many2one(
        related='product_id.categ_id', store=True)
    product_template_id = fields.Many2one(
        related='product_id.product_tmpl_id', store=True)
    qty_product = fields.Float(
        string='Quantity', compute='_compute_qty_product', store=True)
    cost_total = fields.Float(
        compute='_compute_cost_total', string="Cost Total", store=True)

    def _compute_qty_product(self):
        for rec in self:
            rec.qty_product = 0
            moves = self.env['account.move.line'].search([('product_id', '=', rec.product_id.id),
                                                          ('move_id', '=',
                                                           rec.move_id.id),
                                                          ('account_id.account_type', '=', 'income')])
            if moves:
                rec.qty_product = moves[0].quantity

    def _compute_cost_total(self):
        for rec in self:
            rec.cost_total = rec.qty_product * rec.cost_product
