# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    products_in_warehouse = fields.Many2many('product.template', compute='_compute_products_in_warehouse', string='Products in Warehouse')

    @api.depends('warehouse_id')
    def _compute_products_in_warehouse(self):
        for order in self:
            if order.warehouse_id:
                # Find stock quants in the warehouse's stock location
                quants = self.env['stock.quant'].search([
                    ('location_id', 'child_of', order.warehouse_id.lot_stock_id.id),
                    ('quantity', '>', 0.0)
                ])
                # Get the product templates from the quants
                product_templates = quants.mapped('product_id.product_tmpl_id')
                order.products_in_warehouse = [(6, 0, product_templates.ids)]
            else:
                # If no warehouse is selected, all sellable products are available
                all_product_templates = self.env['product.template'].search([('sale_ok', '=', True)])
                order.products_in_warehouse = [(6, 0, all_product_templates.ids)]
