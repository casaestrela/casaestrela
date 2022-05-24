from odoo import _, fields, models


class InventoryValuationReport(models.Model):
    _name = "inventory.valuation.report"
    _description = "Inventory Valuation Report"

    default_code = fields.Char("Default Code")
    name = fields.Many2one("product.product", string="Name")
    category_id = fields.Many2one("product.category", string="Category")
    cost_price = fields.Float("Cost Price")
    beginning = fields.Float("Beginning")
    internal = fields.Float("Internal")
    received = fields.Float("Received")
    sales = fields.Float("Sales")
    adjustment = fields.Float("Adjustment")
    ending = fields.Float("Ending")
    valuation = fields.Float("Valuation")
    stock_move_id = fields.Many2one("stock.move")
