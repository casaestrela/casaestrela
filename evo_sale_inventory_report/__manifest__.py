# coding: utf-8

{
    'name': 'Sale Inventory Reports',
    'version': '14.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'MSP Percentage & MSP Price',
    'depends': [
                'sale_management', 'stock', 'sale_stock',
                ],
    'data': [
        'views/sale_order.xml',
    ],
    'installable': True,
    'application': True,
    'demo': [],
    'test': []
}
