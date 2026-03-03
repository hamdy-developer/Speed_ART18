from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_id', 'company_id', 'order_id.warehouse_id', 'order_id.partner_id')
    def _compute_tax_id(self):
        super()._compute_tax_id()
        for line in self:
            warehouse = line.order_id.warehouse_id
            if warehouse and warehouse.force_warehouse_taxes:
                line.tax_id = warehouse.sale_tax_ids
