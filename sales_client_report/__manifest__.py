# -*- coding: utf-8 -*-
{
    'name': "Sales Client Report",

    'summary': """
        A detailed financial report for client sales, payments, and dues,
        similar to the Partner Ledger but with a specific layout.
    """,

    'description': """
        - Adds a new report under Accounting > Reporting named 'Sales Client Report'.
        - Provides a wizard to filter by date range, partners, and account type (Receivable/Payable).
        - Generates a PDF report grouped by partner with subtotals and a grand total.
    """,

    'author': "Your Name",
    'website': "https://www.yourcompany.com",

    'category': 'Accounting/Accounting',
    'version': '1.0',

    'depends': ['account'],

    'data': [
        'security/ir.model.access.csv',
        'wizard/sales_client_wizard_views.xml',
        'report/sales_client_report_templates.xml',
        'report/sales_client_report_actions.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}