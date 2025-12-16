# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    x_invoice_type = fields.Selection(
        [
            ('customer_invoices', 'فواتير عملاء'),
            ('invoices_without', 'فواتير بدون'),
        ],
        string='Invoice Type',
        help="Customer Invoices: Used for primary warehouses. Invoices Without: Used for secondary warehouses."
    )

