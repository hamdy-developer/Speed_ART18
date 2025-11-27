# -*- coding: utf-8 -*-
{
    'name': 'Bank Reconciliation Wizard',
    'version': '18.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Wizard to open Bank Reconciliation Report with custom filters',
    'description': """
Bank Reconciliation Wizard
===========================
This module adds a wizard to easily access the Bank Reconciliation Report 
with custom filters for date range, partners, and journals.

Features:
---------
* Date range filter (Start Date & End Date)
* Partner filter (Many2many)
* Journal filter (Many2many - Bank journals only)
* Opens the standard Bank Reconciliation Report with applied filters
    """,
    'author': 'Speed ART',
    'depends': ['account', 'account_reports'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/bank_reconciliation_wizard_views.xml',
        'views/bank_reconciliation_menu.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
