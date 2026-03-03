from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    force_warehouse_taxes = fields.Boolean(
        string='Force Warehouse Taxes',
        help='If checked, the system will apply the warehouse taxes to sale and purchase order lines '
             'instead of the product default taxes. If no taxes are selected here, it will result '
             'in 0% tax.'
    )
    sale_tax_ids = fields.Many2many(
        comodel_name='account.tax',
        relation='stock_warehouse_sale_tax_rel',
        column1='warehouse_id',
        column2='tax_id',
        string='Sales Taxes',
        domain=[('type_tax_use', '=', 'sale')]
    )
    purchase_tax_ids = fields.Many2many(
        comodel_name='account.tax',
        relation='stock_warehouse_purchase_tax_rel',
        column1='warehouse_id',
        column2='tax_id',
        string='Purchase Taxes',
        domain=[('type_tax_use', '=', 'purchase')]
    )
