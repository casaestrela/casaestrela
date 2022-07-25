{
    "name": "Evo Multiple Invoice Payment",
    "version": "14.0.1.0",
    "sequence": 104,
    "description": """
        Module will allow multiple invoice payment from payment and invoice screen.
    """,
    "summary": "Module will allow multiple invoice payment from payment and invoice screen.",
    "category": "Accounting Tools",
    "author": "Evozard",
    "website": "http://www.evozard.com",
    "depends": ["sale_management", "account"],
    "data": ["security/ir.model.access.csv", "views/account_payment_view.xml",],
    "installable": True,
    "application": True,
    "auto_install": False,
}
