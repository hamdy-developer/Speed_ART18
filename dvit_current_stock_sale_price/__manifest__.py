# -*- coding: utf-8 -*-
{
    'name': 'DVIT Report current stock with sale price',
    'version': '18.0.0.1',
    'summary': 'Custom module for add new report to get current stock with sale price',
    'description': 'Custom module for add new report to get current stock with sale price ',
    'author': 'DVIT',
    'depends': ['account', 'stock'],
    'data': [

        # Security
        'security/ir.model.access.csv',

        # Views
        'views/stock_quant_report.xml',

    ],

    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,


}
