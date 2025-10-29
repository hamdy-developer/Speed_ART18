{
    'name': "Purchase Return Refund Automation",
    'summary': "Automatically creates a vendor refund when a receipt is returned.",
    'description': """
This module streamlines the return-to-vendor process.
When a return picking for a receipt is validated,
it automatically generates and validates a vendor refund
for the returned quantities.
    """,
    'author': "Gemini",
    'website': "https://www.yourcompany.com",
    'category': 'Inventory/Inventory',
    'version': '1.1',
    'depends': ['stock', 'purchase', 'account'],
    'data': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}