# -*- coding: utf-8 -*-
{
    'name': "Evo Import Product",
    'summary': """Import Product For Odoo 14""",
    'description': """Odoo 14.0 Import Product""",
    'author': "",
    'website': "",    
    'category': 'stock',
    'version': '1.0',
    'depends': ['stock'],

    'data': [
                'security/ir.model.access.csv',    
                'wizard/import_product_wizard_view.xml',
    ],
    'qweb': [
        
    ],
    'images': [],
    'auto_install': False,
    'installable': True,
    'application':True,
}
