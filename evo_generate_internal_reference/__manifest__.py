# -*- coding: utf-8 -*-
{
    'name': "Evo Generate Internal Reference",
    'summary': """Generate Internal Reference For Odoo 14""",
    'description': """Odoo 14.0 Generate Internal Reference""",
    'author': "",
    'website': "",    
    'category': 'stock',
    'version': '1.0',
    'depends': ['product','stock','sale_management','point_of_sale'],

    'data': [
              
        'views/product_category_view.xml',
        'views/operating_unit_view.xml',
    ],
    'qweb': [
        
    ],
    'images': [],
    'auto_install': False,
    'installable': True,
    'application':True,
}
