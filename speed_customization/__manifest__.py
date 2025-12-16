{
    'name': 'Speed Customization',
    'version': '1.0',
    'summary': 'Custom rounding for sale order amounts',
    'description': 'This module applies rounding to price_total in sale.order.line and amount_total in sale.order, and ensures it is reflected in reports.',
    'author': 'Speed',
    'depends': ['sale', 'account', 'purchase', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_warehouse_views.xml',
        'views/purchase_order_views.xml',
        'views/account_journal_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

