# -*- coding: utf-8 -*-

from odoo import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _custom_round(self, value):
        """
        Custom rounding function: Round to nearest whole number (round up or down whichever is closer)
        """
        if value == 0.0:
            return 0.0
        
        # Simple round to nearest whole number
        return round(value)

    @api.depends('order_line.price_subtotal', 'order_line.price_tax', 'order_line.price_total', 'currency_id', 'company_id', 'payment_term_id')
    def _compute_amounts(self):
        """
        Override to apply custom rounding to amount_total and related fields
        Completely override the standard method to sum from rounded line values
        """
        for order in self:
            # Get all order lines (excluding display types)
            order_lines = order.order_line.filtered(lambda x: not x.display_type)
            
            # Sum the already rounded line values
            # These values are already rounded in sale_order_line._compute_amount
            # The @api.depends ensures lines are computed before this method runs
            amount_untaxed = sum(line.price_subtotal for line in order_lines)
            # price_tax is computed in _compute_amount, so it should be available
            amount_tax = sum(line.price_tax for line in order_lines)
            
            # Handle early payment discount if exists
            # This is needed for payment terms with early payment discounts
            if (
                order.payment_term_id
                and order.payment_term_id.early_discount
                and order.payment_term_id.early_pay_discount_computation == 'mixed'
                and order.payment_term_id.discount_percentage
            ):
                # Calculate early payment discount from rounded amounts
                percentage = order.payment_term_id.discount_percentage
                discount_amount = (amount_untaxed / 100) * percentage
                # Apply discount (negative for discount)
                amount_untaxed -= discount_amount
                # Recalculate tax on discounted amount if needed
                # For simplicity, we'll apply the discount proportionally to tax
                if amount_untaxed > 0:
                    tax_ratio = amount_untaxed / (amount_untaxed + discount_amount) if (amount_untaxed + discount_amount) > 0 else 1.0
                    amount_tax = amount_tax * tax_ratio
            
            # Apply custom rounding to ensure totals are rounded
            order.amount_untaxed = self._custom_round(amount_untaxed or 0.0)
            order.amount_tax = self._custom_round(amount_tax or 0.0)
            # Calculate total from rounded values
            order.amount_total = self._custom_round((amount_untaxed + amount_tax) or 0.0)

    def _compute_tax_totals(self):
        """
        Override to update tax_totals with rounded amounts
        """
        # First compute the standard tax_totals structure
        AccountTax = self.env['account.tax']
        for order in self:
            # Ensure amounts are computed first (they should be, but ensure it)
            if not order.amount_untaxed and not order.amount_total:
                order._compute_amounts()
            
            order_lines = order.order_line.filtered(lambda x: not x.display_type)
            base_lines = [line._prepare_base_line_for_taxes_computation() for line in order_lines]
            base_lines += order._add_base_lines_for_early_payment_discount()
            AccountTax._add_tax_details_in_base_lines(base_lines, order.company_id)
            AccountTax._round_base_lines_tax_details(base_lines, order.company_id)
            tax_totals = AccountTax._get_tax_totals_summary(
                base_lines=base_lines,
                currency=order.currency_id or order.company_id.currency_id,
                company=order.company_id,
            )
            
            # Save original unrounded values for ratio calculations
            original_base = tax_totals.get('base_amount_currency', 0.0)
            original_tax = tax_totals.get('tax_amount_currency', 0.0)
            original_total = tax_totals.get('total_amount_currency', 0.0)
            
            # Update the tax_totals with rounded amounts from the order
            # The order amounts are already rounded in _compute_amounts
            # Use the computed order amounts (which are rounded)
            rounded_untaxed = order.amount_untaxed
            rounded_tax = order.amount_tax
            rounded_total = order.amount_total
            
            tax_totals['base_amount_currency'] = rounded_untaxed
            tax_totals['tax_amount_currency'] = rounded_tax
            tax_totals['total_amount_currency'] = rounded_total
            
            # Also update base_amount and total_amount
            # Calculate from currency rate if different from 1.0
            if order.currency_id and order.currency_rate and order.currency_rate != 1.0:
                tax_totals['base_amount'] = rounded_untaxed / order.currency_rate
                tax_totals['tax_amount'] = rounded_tax / order.currency_rate
                tax_totals['total_amount'] = rounded_total / order.currency_rate
            else:
                tax_totals['base_amount'] = rounded_untaxed
                tax_totals['tax_amount'] = rounded_tax
                tax_totals['total_amount'] = rounded_total
            
            # Update subtotals if they exist - use original values for ratio calculation
            if tax_totals.get('subtotals') and original_base != 0:
                base_ratio = rounded_untaxed / original_base if original_base != 0 else 1.0
                tax_ratio = rounded_tax / original_tax if original_tax != 0 else 1.0
                
                for subtotal in tax_totals['subtotals']:
                    # Update subtotal amounts proportionally
                    if 'base_amount_currency' in subtotal:
                        subtotal['base_amount_currency'] = self._custom_round(
                            subtotal['base_amount_currency'] * base_ratio
                        )
                    if 'tax_amount_currency' in subtotal:
                        subtotal['tax_amount_currency'] = self._custom_round(
                            subtotal['tax_amount_currency'] * tax_ratio
                        )
                    # Update local currency amounts if they exist
                    if 'base_amount' in subtotal and order.currency_id and order.currency_rate:
                        subtotal['base_amount'] = subtotal['base_amount_currency'] / order.currency_rate
                    if 'tax_amount' in subtotal and order.currency_id and order.currency_rate:
                        subtotal['tax_amount'] = subtotal['tax_amount_currency'] / order.currency_rate
                    
                    # Update tax groups within subtotals
                    if 'tax_groups' in subtotal:
                        for tax_group in subtotal['tax_groups']:
                            if 'base_amount_currency' in tax_group:
                                tax_group['base_amount_currency'] = self._custom_round(
                                    tax_group['base_amount_currency'] * base_ratio
                                )
                            if 'tax_amount_currency' in tax_group:
                                tax_group['tax_amount_currency'] = self._custom_round(
                                    tax_group['tax_amount_currency'] * tax_ratio
                                )
                            # Update display amounts if they exist
                            if 'display_base_amount_currency' in tax_group:
                                tax_group['display_base_amount_currency'] = self._custom_round(
                                    tax_group['display_base_amount_currency'] * base_ratio
                                )
            
            order.tax_totals = tax_totals

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

