# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'


    x_warehouse_is_secondary = fields.Boolean(
        string='Warehouse is Secondary',
        compute='_compute_warehouse_is_secondary',
        store=True,
        help="True if the warehouse is secondary (فرعي)"
    )

    @api.depends('order_id.picking_type_id.warehouse_id.x_warehouse_type')
    def _compute_warehouse_is_secondary(self):
        """
        Check if the warehouse is secondary (فرعي)
        """
        for line in self:
            if line.order_id and line.order_id.picking_type_id and line.order_id.picking_type_id.warehouse_id:
                warehouse = line.order_id.picking_type_id.warehouse_id
                line.x_warehouse_is_secondary = warehouse.x_warehouse_type == 'secondary'
            else:
                line.x_warehouse_is_secondary = False

    @api.onchange('order_id')
    def _onchange_order_id_warehouse_tax(self):
        """
        Remove taxes when warehouse is secondary (فرعي)
        """
        if self.order_id and self.order_id.picking_type_id and self.order_id.picking_type_id.warehouse_id:
            warehouse = self.order_id.picking_type_id.warehouse_id
            if warehouse.x_warehouse_type == 'secondary':
                # Remove taxes for secondary warehouse
                self.taxes_id = [(5, 0, 0)]  # Remove all taxes

    @api.model_create_multi
    def create(self, vals_list):
        """
        Override create to handle tax logic based on warehouse
        """
        lines = super().create(vals_list)
        # Clear taxes for secondary warehouse after creation
        for line in lines:
            if line.order_id and line.order_id.picking_type_id and line.order_id.picking_type_id.warehouse_id:
                warehouse = line.order_id.picking_type_id.warehouse_id
                if warehouse.x_warehouse_type == 'secondary' and line.taxes_id:
                    # Use ORM with context flag to prevent recursion
                    line.with_context(skip_tax_update=True).write({'taxes_id': [(5, 0, 0)]})
        return lines

    def write(self, vals):
        """
        Override write to handle tax logic when order changes
        """
        # Prevent infinite recursion: skip if we're in a tax update context
        if self.env.context.get('skip_tax_update'):
            return super().write(vals)
        
        result = super().write(vals)
        
        # Only update taxes if order_id changed, and we're not already updating taxes
        if 'taxes_id' not in vals and 'order_id' in vals:
            for line in self:
                if line.order_id and line.order_id.picking_type_id and line.order_id.picking_type_id.warehouse_id:
                    warehouse = line.order_id.picking_type_id.warehouse_id
                    if warehouse.x_warehouse_type == 'secondary' and line.taxes_id:
                        # Use ORM with context flag to prevent recursion
                        line.with_context(skip_tax_update=True).write({'taxes_id': [(5, 0, 0)]})
        return result

