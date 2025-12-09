# -*- coding: utf-8 -*-
{
    'name': "Edit Accses",

    'summary': "Edit Accses",

    'description': """Edit Accses""",

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'sale', 'mrp', 'stock'],

    # always loaded
    'data': [
        'security/edit_access_security.xml',
        'security/ir.model.access.csv',
    ],
}
