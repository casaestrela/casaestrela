# -*- coding: utf-8 -*-
{
    'name': "Evo Auto Generate Invoice From Sale Order",
    'summary': """Auto Generate Invoice From Sale Order For Odoo 14""",
    'description': """Odoo 14.0 Auto Generate Invoice From Sale Order""",
    'author': "",
    'website': "",    
    'category': 'sale',
    'version': '1.0',
    'depends': ['sale_management','account'],

    'data': [
                
            'security/ir.model.access.csv', 
              'wizard/sale_order_confirm_wizard_view.xml',
              'views/sale_order_view.xml',
              'views/account_payment_view.xml',
        
    ],
    'qweb': [
        
    ],
    'images': [],
    'auto_install': False,
    'installable': True,
    'application':True,
}
