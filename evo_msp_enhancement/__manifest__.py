{
    "name": "Evo MSP Enhancement",
    "summary": """MSP Enhancement For Odoo 14""",
    "description": """Odoo 14.0 MSP Enhancement""",
    "author": "",
    "website": "",
    "category": "sale",
    "version": "1.0",
    "depends": [
        "point_of_sale",
        "sale_management",
        "msp_percentage_price",
        "evo_pos_msp",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/res_partner_view.xml",
        "views/sale_view.xml",
        "views/assest.xml",
        "wizard/msp_report_wizard_view.xml",
    ],
    "qweb": ["static/src/xml/msp_allow.xml",],
    "images": [],
    "auto_install": False,
    "installable": True,
    "application": True,
}
