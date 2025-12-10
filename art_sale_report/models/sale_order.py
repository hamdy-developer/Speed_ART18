# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    products_in_warehouse = fields.Many2many('product.template', string='Products in Warehouse',related='order_id.products_in_warehouse')
 
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    products_in_warehouse = fields.Many2many('product.template', compute='_compute_products_in_warehouse', string='Products in Warehouse')
    partner_tags = fields.Many2many(related='partner_id.category_id', string='Partner Tags', readonly=True)
    picking_states = fields.Char(string='Delivery Status', compute='_compute_picking_states')

    @api.depends('picking_ids.state')
    def _compute_picking_states(self):
        for order in self:
            states = order.picking_ids.mapped('state')
            # Translate states
            translated_states = [dict(self.env['stock.picking'].fields_get(allfields=['state'])['state']['selection']).get(s, s) for s in states]
            # Join unique states
            order.picking_states = ', '.join(set(translated_states))

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

    @api.onchange('warehouse_id')
    def _onchange_warehouse_id_for_tax(self):
        tax_free_fp = self.env.ref('art_sale_report.fiscal_position_tax_free', raise_if_not_found=False)
        if not tax_free_fp:
            return

        if self.warehouse_id and self.warehouse_id.x_is_tax_free:
            self.fiscal_position_id = tax_free_fp
        else:
            if self.fiscal_position_id and self.fiscal_position_id.id == tax_free_fp.id:
                # Revert to the default fiscal position for the partner
                self.fiscal_position_id = self.env['account.fiscal.position']._get_fiscal_position(self.partner_id, self.partner_shipping_id)

    @api.onchange('partner_id')
    def onchange_partner_id_warehouse_id(self):
        self._onchange_warehouse_id_for_tax()
        if self.partner_id and self.partner_id.user_id:
            self.user_id = self.partner_id.user_id


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if args is None:
            args = []
        domain=['|',('default_code', operator, name),('name', operator, name)]
        for item in args:
            domain.append(item)
        products=self.search(domain, limit=limit)
        list_products=super().name_search(name, args, operator, limit)
        list_products += [(product.id, product.display_name) for product in products.sudo()]

        seen_ids = set()
        result = []
        for pid, display_name in list_products:
            if pid not in seen_ids:
                seen_ids.add(pid)
                result.append((pid, display_name))
        return result
