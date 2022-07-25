from odoo import api, fields, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    operating_unit_id = fields.Many2one("operating.unit", "Operating Unit")

    @api.model
    def create(self, values):
        res = super(PosOrder, self).create(values)
        if res.session_id.config_id:
            res.operating_unit_id = res.session_id.config_id.operating_unit_id.id
        return res
