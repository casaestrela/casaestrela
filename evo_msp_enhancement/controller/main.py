from odoo import http
from odoo.http import request


class POSConfigMSP(http.Controller):
    @http.route("/update_msp", type="json", auth="none")
    def update_msp(self, config_id, allow_msp, **kwargs):
        pos_config = (
            request.env["pos.config"]
            .sudo()
            .search([("id", "=", config_id["id"])], limit=1)
        )
        if pos_config:
            pos_config.enable_msp = allow_msp
