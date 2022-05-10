# -*- coding: utf-8 -*-
{
    'name': "Evo Casa Enhancement",
    'summary': """Casa Enhancement For Odoo 14""",
    'description': """Odoo 14.0 Casa Enhancement""",
    'author': "",
    'website': "",    
    'category': 'sale',
    'version': '1.0',
    'depends': ['sale_management','sale_margin','evo_msp_enhancement'
                ],

    'data': [
             'security/security.xml',   
            'security/ir.model.access.csv', 
            'views/reason_master_view.xml',
            'views/sale_order_view.xml',
            'views/stock_inventory_view.xml',
            'views/account_move_view.xml',
            'views/delivery.xml',
            'report/report_deliveryslip_with_price.xml',
            'views/stock_picking.xml',
            'views/account_journal_view.xml',
            'views/pos_payment_method_view.xml',
            'views/pos_payment_view.xml',
            'views/stock_scrap_view.xml',
            'views/operating_unit_view.xml',
            'views/analytic_account_view.xml',
            'views/product_pricelist.xml',
            'wizard/partner_ledger_with_product_view.xml',
            'wizard/negative_balance_wizard_view.xml',
            'wizard/account_payment_register_wizard.xml',
            'wizard/import_pricelist_view.xml',
            'wizard/detail_product_report_view.xml',
        
    ],
    'qweb': [
        
    ],
    'images': [],
    'auto_install': False,
    'installable': True,
    'application':True,
}
