# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    x_warehouse_type = fields.Selection(
        [
            ('primary', 'رئيسي'),
            ('secondary', 'فرعي'),
        ],
        string='Warehouse Type',
        help="Primary warehouse: Purchase orders will include taxes. Secondary warehouse: Purchase orders will not have taxes applied.",
        compute='_compute_warehouse_type',
        store=True,
    )

    @api.depends('x_is_tax_free')
    def _compute_warehouse_type(self):
        for record in self:
            record.x_warehouse_type = 'secondary' if record.x_is_tax_free else 'primary'
            