{
    'name': 'Customer Debt Monthly Report',
    'version': '1.0',
    'category': 'Accounting/Reporting',
    'summary': 'Monthly breakdown of customer debt and installments in Excel',
    'description': """
        This module provides a monthly breakdown of customer debt and installments.
        It displays open invoices grouped by partner, showing total values, amounts due,
        and monthly due amounts based on installment dates.
    """,
    'author': 'Antigravity',
    'depends': ['account', 'report_xlsx', 'sales_employee'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/customer_debt_report_wizard_view.xml',
        'report/report_actions.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
