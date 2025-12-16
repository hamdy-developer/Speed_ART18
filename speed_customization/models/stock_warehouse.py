# -*- coding: utf-8 -*-

from odoo import models, fields


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    x_warehouse_type = fields.Selection(
        [
            ('primary', 'رئيسي'),
            ('secondary', 'فرعي'),
        ],
        string='Warehouse Type',
        help="Primary warehouse: Purchase orders will include taxes. Secondary warehouse: Purchase orders will not have taxes applied."
    )

