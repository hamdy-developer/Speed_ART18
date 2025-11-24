# -*- coding: utf-8 -*-
{
    'name': 'Partner Ledger Button',
    'version': '18.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Add smart button to open Partner Ledger from partner form',
    'description': """
        This module adds a smart button on the partner form view
        to quickly access the Partner Ledger report filtered by the current partner.
    """,
    'author': 'Your Company',
    'depends': ['account_reports'],
    'data': [
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
