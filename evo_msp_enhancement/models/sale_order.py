from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    allow_msp = fields.Boolean("Allow MSP", default=True)

    # @api.onchange('partner_id')
    # def onchange_customer_id(self):
    #     for rec in self:
    #         rec.allow_msp = rec.partner_id.allow_msp

    @api.onchange("allow_msp")
    def onchange_allow_msp(self):
        for rec in self:
            for line in rec.order_line:
                line.msp_percentage = (
                    line.product_id.msp_percentage
                    or line.product_id.categ_id.msp_percentage
                )


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends("msp_percentage", "price_subtotal", "price_total")
    def get_msp_subtotal(self):
        res = super(SaleOrderLine, self).get_msp_subtotal()
        for record in self:
            if record.order_id.allow_msp is True:
                record.msp_subtotal = record.price_total - (
                    (record.price_total * record.msp_percentage) / 100
                )
            else:
                record.msp_percentage = 0.0
                record.msp_subtotal = record.price_total - (
                    (record.price_total * record.msp_percentage) / 100
                )
        return res
