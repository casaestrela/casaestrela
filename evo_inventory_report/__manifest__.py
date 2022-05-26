{
    "name": "Evo Inventory Report",
    "summary": """Inventory Report For Odoo 14""",
    "description": """Odoo 14.0 Inventory Report""",
    "author": "Evozard",
    "website": "www.evozard.com",
    "category": "stock",
    "version": "14.0.0.1",
    "depends": ["product", "stock"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/inventory_report_wizard_view.xml",
        "views/inventory_valuation_report_view.xml",
    ],
    "qweb": [],
    "images": [],
    "auto_install": False,
    "installable": True,
    "application": True,
}
