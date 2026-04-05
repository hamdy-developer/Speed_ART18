{
    'name': 'Account Reports - Company Logo on PDF',
    'version': '18.0.1.0.0',
    'summary': 'Add company logo to financial statement PDF reports',
    'description': """
        Adds the company logo to the header of financial statement PDF reports:
        - Profit and Loss
        - Balance Sheet
        - General Ledger
        - Cash Flow Statement
    """,
    'category': 'Accounting/Accounting',
    'author': 'Speed ART',
    'depends': ['account_reports'],
    'data': [
        'data/pdf_export_templates.xml',
    ],
    'assets': {
        'account_reports.assets_pdf_export': [
            'account_reports_logo/static/src/scss/pdf_logo.scss',
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
