# -*- coding: utf-8 -*-
{
    'name': 'DVIT - Inventory at date',
    'version': '18.0',
    'summary': '',
    'description': '',
    'category': 'Inventory',
    'author': 'DVIT',
    'depends': ['stock'],
    'data': [
        # Views
        'views/stock_product_views.xml',
    ],
    #'assets': {
    #    'web.assets_backend': [
    #        'dvit_inventory_at_date/static/src/js/**/*',
    #    ],
    #},
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,

}
