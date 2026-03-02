{
    'name': 'Edit Purchase Speed',
    'version': '1.0',
    'category': 'Purchase',
    'summary': 'Customizations for Purchase module',
    'depends': ['purchase', 'stock', 'product'],
    'data': [
        'views/product_tag_views.xml',
        'views/purchase_order_views.xml',
    ],
    'installable': True,
    'application': False,
}
