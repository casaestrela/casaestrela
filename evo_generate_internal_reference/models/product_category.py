from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    category_prefix = fields.Char("Prefix")
    next_number = fields.Integer("Next Number", default=1)
