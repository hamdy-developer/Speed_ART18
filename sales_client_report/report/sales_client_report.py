# -*- coding: utf-8 -*-
from odoo import models, api, fields
from collections import defaultdict
from datetime import timedelta

class SalesClientReport(models.AbstractModel):
    _name = 'report.sales_client_report.report_sales_client_template'
    _description = 'Sales Client Report Model'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        partner_ids = data.get('partner_ids')
        account_type = data.get('account_type')

        domain = [
            ('invoice_date', '>=', date_from),
            ('invoice_date', '<=', date_to),
            ('state', '=', 'posted'),
        ]

        if account_type == 'receivable':
            domain.append(('move_type', 'in', ('out_invoice', 'out_refund')))
        else: # payable
            domain.append(('move_type', 'in', ('in_invoice', 'in_refund')))

        if partner_ids:
            domain.append(('partner_id', 'in', partner_ids))

        invoices = self.env['account.move'].search(domain, order='partner_id, invoice_date')

        # Use defaultdict to automatically handle new partners
        grouped_invoices = defaultdict(lambda: {'invoices': [], 'subtotal': defaultdict(float)})

        grand_total = defaultdict(float)

        for inv in invoices:
            paid_amount = inv.amount_total - inv.amount_residual
            
            # Calculate remaining due days
            due_days_str = ''
            if inv.invoice_date_due:
                today = fields.Date.context_today(self)
                delta = inv.invoice_date_due - today
                if delta.days >= 0:
                    due_days_str = f"{delta.days} days"
                else:
                    due_days_str = f"{abs(delta.days)} days ago"


            invoice_data = {
                'date': inv.invoice_date,
                'invoice_name': inv.name,
                'sales': inv.amount_untaxed_signed,
                'tax': inv.amount_tax_signed,
                'total_value': inv.amount_total_signed,
                'paid': paid_amount if inv.move_type not in ('out_refund', 'in_refund') else -paid_amount,
                'remaining': inv.amount_residual_signed,
                'due_days': due_days_str,
                'payment_terms': inv.invoice_payment_term_id.name or '',
            }
            
            partner_name = inv.partner_id.name
            grouped_invoices[partner_name]['invoices'].append(invoice_data)
            
            # Update subtotals
            grouped_invoices[partner_name]['subtotal']['sales'] += invoice_data['sales']
            grouped_invoices[partner_name]['subtotal']['tax'] += invoice_data['tax']
            grouped_invoices[partner_name]['subtotal']['total_value'] += invoice_data['total_value']
            grouped_invoices[partner_name]['subtotal']['paid'] += invoice_data['paid']
            grouped_invoices[partner_name]['subtotal']['remaining'] += invoice_data['remaining']
        
        # Calculate grand totals from subtotals
        for partner in grouped_invoices.values():
            grand_total['sales'] += partner['subtotal']['sales']
            grand_total['tax'] += partner['subtotal']['tax']
            grand_total['total_value'] += partner['subtotal']['total_value']
            grand_total['paid'] += partner['subtotal']['paid']
            grand_total['remaining'] += partner['subtotal']['remaining']

        return {
            'doc_ids': docids,
            'doc_model': 'sales.client.wizard',
            'data': data,
            'grouped_invoices': grouped_invoices,
            'grand_total': grand_total,
        }