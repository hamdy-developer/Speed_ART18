# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    total_cost = fields.Float(compute='_compute_total_cost_sale_price', compute_sudo=False, search='_search_total_cost')
    total_sale_price = fields.Float(compute='_compute_total_cost_sale_price', compute_sudo=False, search='_search_total_sale_price')

    @api.depends('qty_available', 'lst_price', 'standard_price')
    def _compute_total_cost_sale_price(self):
        for product in self:
            product.total_cost = product.standard_price * product.qty_available
            product.total_sale_price = product.lst_price * product.qty_available


    def _search_total_cost(self, operator, value):
        # TDE FIXME: should probably clean the search methods
        return self._search_product_quantity(operator, value, 'total_cost')
    def _search_total_sale_price(self, operator, value):
        # TDE FIXME: should probably clean the search methods
        return self._search_product_quantity(operator, value, 'total_sale_price')
