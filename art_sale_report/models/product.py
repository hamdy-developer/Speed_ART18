# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    x_brand = fields.Char('Brand')
    pricelist_price = fields.Float(
        string='Pricelist Price',
        compute='_compute_pricelist_price',
    )

    @api.depends('list_price')
    def _compute_pricelist_price(self):
        for product in self:
            # Get all pricelist items for this product
            pricelist_items = self.env['product.pricelist.item'].search([
                ('product_tmpl_id', '=', product.id),
                ('applied_on', '=', '1_product'),
            ], limit=1, order='fixed_price asc')
            
            if pricelist_items:
                product.pricelist_price = pricelist_items[0].fixed_price
            else:
                product.pricelist_price = product.list_price
