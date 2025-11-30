# -*- coding: utf-8 -*-

import logging
from ast import literal_eval

from psycopg2 import Error

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools import check_barcode_encoding, groupby
from odoo.tools.float_utils import float_compare, float_is_zero

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    standard_price = fields.Float(
        'Cost', company_dependent=True, store=True,
        digits='Product Price',
        groups="base.group_user",
        help="""In Standard Price & AVCO: value of the product (automatically computed in AVCO).
        In FIFO: value of the next unit that will leave the stock (automatically computed).
        Used to value the product when the purchase cost is not known (e.g. inventory adjustment).
        Used to compute margins on sale orders.""")


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    standard_price = fields.Float(
        'Cost', compute='_compute_standard_price',
        inverse='_set_standard_price', search='_search_standard_price',
        digits='Product Price', groups="base.group_user", store=True,
        help="""In Standard Price & AVCO: value of the product (automatically computed in AVCO).
        In FIFO: value of the next unit that will leave the stock (automatically computed).
        Used to value the product when the purchase cost is not known (e.g. inventory adjustment).
        Used to compute margins on sale orders.""")


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    product_tmpl_id = fields.Many2one(
        'product.template', string='Product Template',
        related='product_id.product_tmpl_id', store=True)
    product_categ_id = fields.Many2one(
        related='product_tmpl_id.categ_id', store=True)
    inventory_quantity_auto_apply = fields.Float(
        'Inventoried Quantity', digits='Product Unit of Measure',
        compute='_compute_inventory_quantity_auto_apply',
        inverse='_set_inventory_quantity', groups='stock.group_stock_manager',
        store=True
    )
    standard_price = fields.Float(
        related='product_id.standard_price')


class StockQuantReport(models.Model):
    _name = 'stock.quant.report.price'
    _auto = False
    _description = 'Quants Report'
    _rec_name = 'product_id'

    def _domain_product_id(self):
        domain = [('type', '=', 'product')]
        if self.env.context.get('product_tmpl_ids') or self.env.context.get('product_tmpl_id'):
            products = self.env.context.get(
                'product_tmpl_ids', []) + [self.env.context.get('product_tmpl_id', 0)]
            domain = expression.AND(
                [domain, [('product_tmpl_id', 'in', products)]])
        return domain

    def _domain_location_id(self):
        return [('usage', 'in', ['internal', 'transit'])]

    product_id = fields.Many2one(
        'product.product', 'Product',
        domain=lambda self: self._domain_product_id(),
        ondelete='restrict', required=True, index=True, check_company=True)
    product_tmpl_id = fields.Many2one(
        'product.template', string='Product Template')
    product_categ_id = fields.Many2one('product.category',)
    standard_price = fields.Float(string="Cost")
    price_unit = fields.Float()
    product_qty = fields.Float(string='Quantity')

    cost_total = fields.Float(string="Cost Total")
    price_subtotal = fields.Float(string="Price Subtotal")

    location_id = fields.Many2one(
        'stock.location', 'Location',
        domain=lambda self: self._domain_location_id(),
        auto_join=True, ondelete='restrict', required=True, index=True, check_company=True, )

    def _select(self):
        return """
            SELECT
                sq.id,
                sq.product_id,
                sq.product_tmpl_id,
                pt.categ_id as product_categ_id,
                sq.inventory_quantity_auto_apply - sq.reserved_quantity as product_qty,
                sq.location_id,
                pt.list_price as price_unit,
                pt.standard_price as standard_price,  -- تعديل لاستخدام standard_price من product_template
                sq.inventory_quantity_auto_apply * pt.list_price AS price_subtotal,
                sq.inventory_quantity_auto_apply * pt.standard_price AS cost_total
        """

    def _from(self):
        return """
            FROM stock_quant as sq
            LEFT JOIN product_template as pt ON pt.id = sq.product_tmpl_id
        """

    def _where(self):
        return """

        """

    def _group_by(self):
        return """
            GROUP BY
                sq.id,
                pt.categ_id,
                sq.product_id,
                sq.product_tmpl_id,                
                sq.location_id,
                pt.list_price,
                pt.standard_price  -- تعديل لاستخدام standard_price من product_template
        """

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                %s
                %s
                %s
                %s
            )
        """ % (self._table, self._select(), self._from(), self._where(), self._group_by()))
