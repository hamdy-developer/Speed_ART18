{
    'name': 'Payment Term Pricelist',
    'summary': 'Link pricelists to payment terms and apply them automatically on sales orders.',
    'description': """
        This module extends Odoo's functionality by allowing users to associate a specific
        pricelist with a payment term. When a payment term with an associated pricelist
        is selected on a sales order, the sales order's pricelist is automatically updated.

        Key Features:
        - Add 'Change Pricelist' boolean field to Payment Terms.
        - Add 'Pricelist' Many2one field to Payment Terms, conditionally visible.
        - Automatically update Sales Order pricelist based on selected Payment Term.
    """,
    'author': 'Gemini',
    'website': 'https://www.yourcompany.com',
    'category': 'Sales/Sales',
    'version': '1.0',
    'depends': ['account', 'sale', 'product'],
    'data': [
        'views/account_payment_term_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}