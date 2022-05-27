{
    "name": "Purchase Order Automation",
    "version": "14.0",
    "author": "Evozard",
    "category": "Purchase",
    "summary": """Enable auto purchase workflow with purchase order 
                  confirmation. Include operations like Auto Create Invoice, 
                  Auto Validate Invoice and Auto Transfer Delivery Order.""",
    "description": """
        You can directly create invoice and set done to delivery order by single
         click
    """,
    "website": "www.evozard.com",
    "depends": ["purchase", "stock", "stock_operating_unit"],
    "data": ["views/stock_warehouse.xml"],
    "installable": True,
    "application": True,
    "auto_install": False,
    #     'images': ['static/description/main_screen.png'],
}
