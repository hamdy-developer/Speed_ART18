# -*- coding: utf-8 -*-

from odoo import models, api
from decimal import Decimal, ROUND_HALF_UP
import math


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _custom_round(self, value):
        """
        Custom rounding function:
        - If decimal part < 0.50: round down to whole number (floor)
        - If decimal part >= 0.50: use ROUND_HALF_UP (rounding half away from zero)
        """
        if value == 0.0:
            return 0.0
        
        # Get the decimal part
        decimal_part = abs(value) - math.floor(abs(value))
        
        if decimal_part < 0.50:
            # Round down to whole number
            return math.floor(value) if value >= 0 else math.ceil(value)
        else:
            # Use ROUND_HALF_UP (rounding half away from zero)
            return float(Decimal(str(value)).quantize(Decimal('1'), rounding=ROUND_HALF_UP))

    def _amount_all(self):
        """
        Override to apply custom rounding to amount_total and related fields
        Recalculate totals from rounded line totals to ensure consistency
        """
        super()._amount_all()
        for order in self:
            # Recalculate from rounded line totals
            amount_untaxed = sum(line.price_subtotal for line in order.order_line)
            amount_tax = sum(getattr(line, 'price_tax', 0.0) for line in order.order_line)
            
            # Apply custom rounding
            order.amount_untaxed = self._custom_round(amount_untaxed or 0.0)
            order.amount_tax = self._custom_round(amount_tax or 0.0)
            
            # Calculate amount_total from rounded values
            order.amount_total = order.amount_untaxed + order.amount_tax

    def _prepare_invoice(self):
        """
        Override to set journal based on warehouse type
        """
        invoice_vals = super()._prepare_invoice()
        
        # Get the warehouse from the sale order
        if self.warehouse_id and self.warehouse_id.x_warehouse_type:
            warehouse_type = self.warehouse_id.x_warehouse_type
            
            # Determine which journal type to use
            if warehouse_type == 'primary':
                # Primary warehouse: use journal with "فواتير عملاء"
                journal_type = 'customer_invoices'
            elif warehouse_type == 'secondary':
                # Secondary warehouse: use journal with "فواتير بدون"
                journal_type = 'invoices_without'
            else:
                journal_type = None
            
            # Find the appropriate journal
            if journal_type:
                journal = self.env['account.journal'].search([
                    ('type', '=', 'sale'),
                    ('x_invoice_type', '=', journal_type),
                    ('company_id', '=', self.company_id.id),
                ], limit=1)
                
                if journal:
                    invoice_vals['journal_id'] = journal.id
                else:
                    # If no journal found with the specific type, log a warning but continue
                    # The default journal will be used
                    pass
        
        return invoice_vals

