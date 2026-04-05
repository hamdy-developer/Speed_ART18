from odoo import models, fields, api

class VendorEvaluationReport(models.TransientModel):
    _name = 'vendor.evaluation.report'
    _description = 'Vendor Evaluation Report'

    product_id = fields.Many2one('product.product', string='Product')
    product_tmpl_id = fields.Many2one('product.template', string='Product Template')
    product_brand_id = fields.Many2one('product.brand', string='Product Brand')
    vendor_id = fields.Many2one('res.partner', string='Vendor')
    total_purchase_cost = fields.Float(string='Total Purchase Cost')
    total_sales = fields.Float(string='Total Sales')
    stock_amount = fields.Float(string='Stock Amount')
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure')

    @api.model
    def _compute_data(self):
        # Clear previous records for this user to avoid stale data
        self.search([('create_uid', '=', self.env.user.id)]).unlink()

        # Data Sourcing - Purchases
        domain_purchases = [
            ('move_id.move_type', 'in', ['in_invoice', 'in_refund']), 
            ('product_id', '!=', False), 
            ('parent_state', '=', 'posted')
        ]
        purchase_groups = self.env['account.move.line'].read_group(
            domain_purchases, 
            ['product_id', 'move_id.move_type:type', 'price_subtotal:sum'], 
            ['product_id', 'move_id.move_type']
        )
        purchase_data = {}
        for res in purchase_groups:
            pid = res['product_id'][0] if res.get('product_id') else False
            if not pid: continue
            val = res['price_subtotal']
            # Refunds decrease the total purchase cost
            if res.get('move_id.move_type') == 'in_refund':
                val = -val
            purchase_data[pid] = purchase_data.get(pid, 0.0) + val

        # Data Sourcing - Sales
        domain_sales = [
            ('move_id.move_type', 'in', ['out_invoice', 'out_refund']), 
            ('product_id', '!=', False), 
            ('parent_state', '=', 'posted')
        ]
        sales_groups = self.env['account.move.line'].read_group(
            domain_sales, 
            ['product_id', 'move_id.move_type:type', 'price_subtotal:sum'], 
            ['product_id', 'move_id.move_type']
        )
        sales_data = {}
        for res in sales_groups:
            pid = res['product_id'][0] if res.get('product_id') else False
            if not pid: continue
            val = res['price_subtotal']
            # Refunds decrease the total sales
            if res.get('move_id.move_type') == 'out_refund':
                val = -val
            sales_data[pid] = sales_data.get(pid, 0.0) + val

        # Collect all relevant products
        all_product_ids = set()
        all_product_ids.update(purchase_data.keys())
        all_product_ids.update(sales_data.keys())

        # Include products with available stock
        products_with_stock = self.env['product.product'].search([('qty_available', '>', 0)])
        all_product_ids.update(products_with_stock.ids)

        records_to_create = []
        products = self.env['product.product'].browse(list(all_product_ids))
        for product in products:
            # Vendor Determination
            vendor_id = False
            seller = product.seller_ids[:1]
            if seller:
                vendor_id = seller.partner_id.id
            elif hasattr(product, 'last_purchase_supplier_id') and product.last_purchase_supplier_id:
                vendor_id = product.last_purchase_supplier_id.id
            
            # Brand Determination
            brand_id = False
            if hasattr(product, 'product_brand_id') and product.product_brand_id:
                brand_id = product.product_brand_id.id
            elif hasattr(product.product_tmpl_id, 'product_brand_id') and product.product_tmpl_id.product_brand_id:
                brand_id = product.product_tmpl_id.product_brand_id.id
                
            records_to_create.append({
                'product_id': product.id,
                'product_tmpl_id': product.product_tmpl_id.id,
                'product_brand_id': brand_id,
                'vendor_id': vendor_id,
                'total_purchase_cost': purchase_data.get(product.id, 0.0),
                'total_sales': sales_data.get(product.id, 0.0),
                'stock_amount': product.qty_available,
                'uom_id': product.uom_id.id,
            })
            
        # Create records
        if records_to_create:
            self.create(records_to_create)

    @api.model
    def action_generate_report(self):
        """Server Action entry point that computes data and opens the tree view."""
        self._compute_data()
        
        tree_view_id = self.env.ref('edit_account.vendor_evaluation_report_tree_view', raise_if_not_found=False)
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vendor Evaluation Report',
            'view_mode': 'list', # Note: Odoo 16+ uses 'list' for tree view action modes
            'res_model': 'vendor.evaluation.report',
            'domain': [('create_uid', '=', self.env.user.id)],
            'views': [(tree_view_id.id if tree_view_id else False, 'list')],
            'context': {
                'group_by': ['vendor_id']
            },
        }
