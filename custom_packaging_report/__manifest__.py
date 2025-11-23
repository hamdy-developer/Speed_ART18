# -*- coding: utf-8 -*-
{
    'name': 'Custom Product Packaging Report (XLSX)',
    'version': '1.0',
    'category': 'Inventory/Reporting',
    'summary': 'Generates an XLSX report for on-hand quantities based on packaging units.',
    'depends': ['stock', 'base_automation'], # أضفنا base_automation
    'data': [
        'security/ir.model.access.csv',
        'views/wizard_view.xml',
        'views/menu.xml',
        # لم نعد بحاجة لملفات التقرير الخاصة بـ PDF
    ],
    'installable': True,
    'application': False,
}