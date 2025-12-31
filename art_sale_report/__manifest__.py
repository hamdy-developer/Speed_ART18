{
    'name': 'ART Sale Report',
    'version': '1.0',
    'summary': 'Custom sale order report for Arab Royal Trading',
    'description': 'This module provides a custom sale order report in the format requested by ART.',
    'author': 'Gemini',
    'depends': ['sale', 'product', 'stock', 'account', 'sale_stock', 'purchase','sale_discount_display_amount'],
    'data': [
        'security/ir.model.access.csv',
        'data/fiscal_position_data.xml',
        'report/sale_report.xml',
        'report/sale_report_template.xml',
        'report/sale_report_quotation_template.xml',
        'views/product_views.xml',
        'views/sale_order_view.xml',
        'views/sale_menus.xml',
        'views/purchase_menus.xml',
        'views/stock_warehouse_view.xml',

    ],
    'assets': {
        'web.report_assets_common': [
            'art_sale_report/static/src/css/report.css',
        ],
    },
    'installable': True,
    'application': False,
}
