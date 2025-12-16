# -*- coding: utf-8 -*-

from odoo import models, api
from decimal import Decimal, ROUND_HALF_UP
import math


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _custom_round(self, value):
        """
        Custom rounding function: Round to nearest whole number (round up or down whichever is closer)
        """
        if value == 0.0:
            return 0.0
        
        # Simple round to nearest whole number
        return round(value)

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Override to apply custom rounding to price_total and related fields
        """
        for line in self:
            base_line = line._prepare_base_line_for_taxes_computation()
            self.env['account.tax']._add_tax_details_in_base_line(base_line, line.company_id)
            
            # Get raw values from tax computation
            raw_subtotal = base_line['tax_details']['raw_total_excluded_currency']
            raw_total = base_line['tax_details']['raw_total_included_currency']
            raw_tax = raw_total - raw_subtotal
            
            # Apply custom rounding to all values
            line.price_subtotal = self._custom_round(raw_subtotal or 0.0)
            line.price_tax = self._custom_round(raw_tax or 0.0)
            line.price_total = self._custom_round(raw_total or 0.0)

    # def _compute_amount(self):
    #     """
    #     Override to apply rounding to price_total and related fields
    #     """
    #     super()._compute_amount()
    #     for line in self:
    #         # Round price_subtotal to 2 decimal places using standard rounding
    #         price_subtotal = float(Decimal(str(line.price_subtotal or 0.0)).quantize(
    #             Decimal('0.01'), rounding=ROUND_HALF_UP))
    #         line.price_subtotal = price_subtotal
    #
    #         # Round price_tax if it exists
    #         price_tax = 0.0
    #         if hasattr(line, 'price_tax') and line.price_tax:
    #             price_tax = float(Decimal(str(line.price_tax)).quantize(
    #                 Decimal('0.01'), rounding=ROUND_HALF_UP))
    #             line.price_tax = price_tax
    #
    #         # Round price_total to 2 decimal places (sum of subtotal + tax)
    #         price_total = float(Decimal(str(price_subtotal + price_tax)).quantize(
    #             Decimal('0.01'), rounding=ROUND_HALF_UP))
    #         line.price_total = price_total

