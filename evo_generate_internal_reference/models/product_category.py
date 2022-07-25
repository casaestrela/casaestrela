from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ProductCategory(models.Model):
    _inherit = "product.category"

    category_prefix = fields.Char("Prefix")
    next_number = fields.Integer("Next Number", default=1)
