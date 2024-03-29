{
    "name": "Evo Operating Unit Access Right",
    "summary": "Evo Operating Unit Access Right",
    "category": "tools",
    "version": "14.0",
    "author": "Evozard",
    "website": "www.evozard.com",
    "depends": [
        "stock_operating_unit",
        "operating_unit",
        "account_operating_unit",
        "point_of_sale",
        "dynamic_accounts_report",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/stock_picking_view.xml",
    ],
    "qweb": [],
    "installable": True,
    "auto_install": False,
    "application": False,
    "sequence": 107,
}
