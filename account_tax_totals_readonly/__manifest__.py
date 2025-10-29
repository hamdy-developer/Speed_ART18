{
    'name': 'Account Tax Totals Readonly',
    'version': '1.0',
    'summary': 'Make tax totals readonly in invoices.',
    'author': 'Gemini',
    'depends': ['account'],
    'assets': {
        'web.assets_backend': [
            'account_tax_totals_readonly/static/src/components/tax_totals/tax_totals.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}