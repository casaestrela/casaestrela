# -*- coding: utf-8 -*-
{
    'name': "Evo MSP In Point Of Sale",
    'summary': """MSP In Point Of Sale For Odoo 14""",
    'description': """Odoo 14.0 MSP In Point Of Sale""",
    'author': "",
    'website': "",    
    'category': 'stock',
    'version': '1.0',
    'depends': ['point_of_sale','msp_percentage_price'],

    'data': [
              'views/assests.xml',
              'views/pos_config_view.xml',
              'views/pos_order_line.xml',
              'views/sale_order_view.xml',
    ],
    'qweb': [
        
    ],
    'images': [],
    'auto_install': False,
    'installable': True,
    'application':True,
}
