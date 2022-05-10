# -*- coding: utf-8 -*-
{
    'name': "Evo Validate Order Without Payment In POint Of Sale",
    'summary': """Validate Order Without Payment In POint Of Sale For Odoo 14""",
    'description': """Odoo 14.0 Validate Order Without Payment In POint Of Sale""",
    'author': "",
    'website': "",    
    'category': 'stock',
    'version': '1.0',
    'depends': ['point_of_sale'],

    'data': [
            'views/assests.xml',
    ],
    'qweb': [
        'static/src/xml/Paymentscreen.xml',
    ],
    'images': [],
    'auto_install': False,
    'installable': True,
    'application':True,
}