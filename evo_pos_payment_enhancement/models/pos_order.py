from odoo import api, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def create(self, values):
        values["state"] = "paid"
        return super(PosOrder, self).create(values)
