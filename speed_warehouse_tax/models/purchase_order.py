from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.onchange('picking_type_id')
    def _onchange_picking_type_id_update_taxes(self):
        for order in self:
            for line in order.order_line:
                line._compute_tax_id()


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _compute_tax_id(self):
        super()._compute_tax_id()
        for line in self:
            picking_type = line.order_id.picking_type_id
            print(f"DEBUG Speed: _compute_tax_id called for line {line.name}, picking_type: {picking_type.name if picking_type else None}")
            if picking_type and picking_type.warehouse_id:
                warehouse = picking_type.warehouse_id
                print(f"DEBUG Speed: warehouse {warehouse.name}, force: {warehouse.force_warehouse_taxes}, taxes: {warehouse.purchase_tax_ids.ids}")
                if warehouse.force_warehouse_taxes:
                    line.taxes_id = [(6, 0, warehouse.purchase_tax_ids.ids)]

