{
    "name": "Sale with Multiple Operating Unit",
    "summary": "Allow a unit to request internal quotes to another",
    "version": "14.0.1.0.0",
    "author": "Evozard",
    "website": "http://www.evozard.com",
    "category": "Sales Management",
    "depends": [
        "crm",
        "product_operating_unit",
        "res_partner_operating_unit",
        "sale_operating_unit",
    ],
    "license": "AGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "security/ir_rule.xml",
        "views/res_company.xml",
        "views/sale_order_view.xml",
    ],
    "development_status": "Beta",
    "maintainers": ["max3903"],
}
