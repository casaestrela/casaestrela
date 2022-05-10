# -*- coding: utf-8 -*-
{
    'name': "Evo Inventory Report",
    'summary': """Inventory Report For Odoo 14""",
    'description': """Odoo 14.0 Inventory Report""",
    'author': "",
    'website': "",    
    'category': 'stock',
    'version': '1.0',
    'depends': ['product','stock',],

    'data': [
              'security/ir.model.access.csv', 
              'wizard/inventory_report_wizard_view.xml',
              'views/inventory_valuation_report_view.xml',
    ],
    'qweb': [
        
    ],
    'images': [],
    'auto_install': False,
    'installable': True,
    'application':True,
}
