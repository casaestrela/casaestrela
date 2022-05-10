# -*- coding: utf-8 -*-
{
    'name': "Casa Fund Transfer Enhancement",
    'summary': """Casa Fund Transfer Enhancement.""",
    'description': """Odoo 14.0 Casa Enhancement""",
    'author': "Evozard",
    'website': "www.evozard.com",
    'category': 'account',
    'version': '14.0.0.1',
    'depends': ['account','sales_team','operating_unit'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/operating_unit_view.xml',
        'views/fund_transfer_view.xml',
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}
