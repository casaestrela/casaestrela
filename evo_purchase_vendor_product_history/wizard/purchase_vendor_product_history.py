from odoo import api, fields, models


class ProductPurchaseHistoryWizard(models.TransientModel):
    _name = "product.purchase.order.history"
    _description = "Product Purchase History"
    _rec_name = "product_id"

    product_purchase_history = fields.One2many(
        "product.purchase.history.line",
        "order_line_id",
        string="Product Purchase Price History",
        help="shows the product Purchase history of the vendor",
    )
    product_id = fields.Many2one("product.product", string="Product:")


class PurchasePriceHistory(models.TransientModel):
    _name = "product.purchase.history.line"
    _description = "Product Purchase History Line"
    _rec_name = "purchase_order_id"

    order_line_id = fields.Many2one("product.purchase.order.history")
    vendor_id = fields.Many2one("res.partner", string="Vendor")
    order_date = fields.Date("Date")
    purchase_order_id = fields.Many2one("purchase.order", string="Order")
    history_price = fields.Char(string="Unit Price")
    history_qty = fields.Float(string="Quantity")
    history_total = fields.Float(string="Total")
