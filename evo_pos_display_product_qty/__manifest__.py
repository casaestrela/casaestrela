# -*- coding: utf-8 -*-
{
    'name': 'Evo POS Display Product Qty',
    'summary': 'Evo POS Display Product Qty',
    'category': 'tools',
    'version': '14.0',
    'author': 'Evozard',
    'website': 'www.evozard.com',
    'depends': [
        'point_of_sale',
    ],
    'data': [
        
        
        'views/product_view.xml',
        'views/pos_assest.xml',
        'views/sale_view.xml',
        'views/pos_config_view.xml',
        
        
    ],
    'qweb': [
        'static/src/xml/pos_template.xml',
        ],
    'images': ["static/description/banner.jpg"],
    'installable': True,
    'auto_install': False,
    'application': False,
    'sequence': 107,
}
