# -*- coding: utf-8 -*-

from odoo import models, fields

class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    x_is_tax_free = fields.Boolean(string='Tax Free Warehouse', help="If checked, sales from this warehouse will not have taxes applied.")
