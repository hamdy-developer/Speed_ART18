# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    x_warehouse_id = fields.Many2one(
        related='order_id.picking_type_id.warehouse_id',
        string='Warehouse Helper',
    )
