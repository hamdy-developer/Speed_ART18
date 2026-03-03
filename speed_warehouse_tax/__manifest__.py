{
    'name': 'Speed Warehouse Tax',
    'version': '18.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Apply specific taxes based on the selected Warehouse in Sale and Purchase Orders.',
    'description': """
        This module allows users to configure specific taxes (sales and purchases) directly on the Warehouse.
        When a warehouse is selected in a Sale Order or a Picking Type is selected in a Purchase Order,
        the system will automatically apply these configured taxes to the order lines.
        If the warehouse has the 'Force Warehouse Taxes' option enabled but no taxes are selected,
        the order lines will have 0% tax.
    """,
    'author': 'Speed',
    'depends': [
        'stock',
        'sale_management',
        'purchase',
    ],
    'data': [
        # 'security/ir.model.access.csv',
        'views/stock_warehouse_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
