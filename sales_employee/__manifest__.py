# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Sales Employee',
    'version': '18.0.1.0.0',
    'category': 'Sales/Sales',
    'summary': 'Add Sales Employee field across CRM Team, Contacts, Sales Orders and Invoices',
    'description': """
Sales Employee Module
=====================
This module adds Sales Employee functionality:
- CRM Team: New tab "Sales Employees" to add employees from hr.employee
- Contact: New field "Sales Employee" beside the salesperson field  
- Sale Order: New field that auto-fetches Sales Employee from customer
- Invoice: Displays Sales Employee from the related Sale Order
    """,
    'author': 'Speed ART',
    'depends': ['sale', 'hr', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/crm_team_views.xml',
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
