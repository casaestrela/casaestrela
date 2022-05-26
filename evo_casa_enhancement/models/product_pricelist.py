from odoo import fields, models


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    pricelist_processed_log_ids = fields.One2many(
        "pricelist.process.log", "pricelist_id", string="Processed Log"
    )
