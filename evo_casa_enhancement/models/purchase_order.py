from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.onchange("operating_unit_id")
    def onchange_operating_unit_id_value(self):
        if self.operating_unit_id:
            partner_ids = []
            partner_unit_check = self.env["res.partner"].search([])
            if partner_unit_check:
                for vendor_line in partner_unit_check:
                    if vendor_line.operating_unit_ids:
                        if self.operating_unit_id in vendor_line.operating_unit_ids:
                            partner_ids.append(vendor_line.id)
            return {"domain": {"partner_id": [("id", "in", partner_ids)]}}
        else:
            return {"domain": {"partner_id": [("id", "in", [])]}}
