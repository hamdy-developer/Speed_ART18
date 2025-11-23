{
    "name": "Product Movement Report",
    "version": "18.0",
    "author": "DVIT",
    "category": "Inventory",
    "summary": "Generate reports for product movements grouped by location and month.",
    "license": "AGPL-3",
    "depends": ["base", "stock", "report_xlsx"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/product_movement_wizard_view.xml",
        "views/product_movement_tree_view.xml",
        "reports/product_movement_pdf_template.xml",
        "reports/product_movement_report.xml"
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
