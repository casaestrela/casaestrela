{
    "name": "Evo POS Operating Unit",
    "category": "Tools",
    "sequence": 55,
    "summary": "Evo POS Operating Unit",
    "author": "Evozard",
    "website": "http://evozard.com/",
    "version": "14.0.1",
    "description": "Get the Detail Of POS Operating Unit.",
    "depends": ["point_of_sale", "account_operating_unit"],
    "data": [
        "views/pos_order_view.xml",
        "views/pos_config_view.xml",
        "views/account_move.xml",
        "views/pos_payment_view.xml",
    ],
    "installable": True,
    "application": True,
}
