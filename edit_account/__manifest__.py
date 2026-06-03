{
    'name': "edit_account",

    'summary': "Add ETA partner to invoice and credit limit functionality",
    'depends': ['base', 'account', 'sale', 'product', 'stock', 'purchase', 'sale_management', 'product_brand'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'report/invoice_report.xml',
        'report/invoice_report_template.xml',
        'report/bank_statement_line_report.xml',
        'report/bank_statement_line_report_template.xml',
        'report/account_invoice_report_view.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/vendor_evaluation_report_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

