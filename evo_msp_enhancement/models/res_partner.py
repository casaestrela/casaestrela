from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    allow_msp = fields.Boolean("Allow MSP")

    @api.model
    def default_get(self, field_list):
        res = super(ResPartner, self).default_get(field_list)
        user = self.env.user
        res.update(
            {
                "property_product_pricelist": user.default_operating_unit_id.pricelist_id.id,
            }
        )

        return res
