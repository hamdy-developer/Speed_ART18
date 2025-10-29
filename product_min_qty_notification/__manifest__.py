{
    'name': "Product Minimum Quantity Notification",

    'summary': "Send notification when product quantity is below minimum",

    'description': """
        This module adds a minimum quantity field to the product and sends a notification to a specific group of users when the on-hand quantity of a product is below the minimum quantity.
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    'category': 'Inventory',
    'version': '0.1',

    'depends': ['stock'],

    'data': [
        'security/ir.model.access.csv',
        'views/product_views.xml',
        'data/cron.xml',

        'security/security.xml',
    ],
}
