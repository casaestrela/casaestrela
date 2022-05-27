from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    msp_percentage = fields.Float("MSP Percentage")
    msp_subtotal = fields.Float("MSP Subtotal", compute="_get_msp_subtotal")

    @api.depends("msp_percentage", "price_subtotal", "price_total")
    def _get_msp_subtotal(self):
        for record in self:
            # record.msp_subtotal = record.price_subtotal - ((record.price_subtotal * record.msp_percentage) / 100)
            record.msp_subtotal = record.price_total - (
                (record.price_total * record.msp_percentage) / 100
            )

    @api.onchange("product_id")
    def _onchange_product_id(self):
        super(AccountMoveLine, self)._onchange_product_id()
        for line in self:
            line.msp_percentage = (
                line.product_id.msp_percentage
                or line.product_id.categ_id.msp_percentage
            )
