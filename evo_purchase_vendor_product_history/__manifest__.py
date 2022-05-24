# -*- coding: utf-8 -*-
{
    'name': "Evo Purchase Vendor Product History",
    'summary': """Purchase Vendor Product History For Odoo 14""",
    'description': """Odoo 14.0 Purchase Vendor Product History""",
    'author': "",
    'website': "",    
    'category': 'purchase',
    'version': '1.0',
    'depends': ['purchase'],

    'data': [
                'security/ir.model.access.csv',    
                'views/purchase_order_view.xml',
                'wizard/purchase_vendor_product_history.xml',
    ],
    'qweb': [
        
    ],
    'images': [],
    'auto_install': False,
    'installable': True,
    'application':True,
}
