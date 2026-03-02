# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductTag(models.Model):
    _inherit = 'product.tag'

    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
