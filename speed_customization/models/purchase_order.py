# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.onchange('picking_type_id')
    def _onchange_picking_type_id_warehouse_tax(self):
        """
        Update order lines taxes when picking type (warehouse) changes
        """
        if self.picking_type_id and self.picking_type_id.warehouse_id:
            warehouse = self.picking_type_id.warehouse_id
            if warehouse.x_warehouse_type == 'secondary':
                # Remove taxes from all lines for secondary warehouse
                for line in self.order_line:
                    if line.taxes_id:
                        line.taxes_id = [(5, 0, 0)]

