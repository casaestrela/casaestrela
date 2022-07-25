from odoo import fields, models


class pos_config(models.Model):
    _inherit = "pos.config"

    show_qty_on_pos = fields.Boolean(string="Display Stock in POS", default=True)
    restric_product_sale = fields.Boolean(
        string="Restric Product Out Of Stock", default=True
    )
