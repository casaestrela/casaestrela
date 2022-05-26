from odoo import http
from odoo.http import request


class POSConfigMSP(http.Controller):
    @http.route("/get_operating_unit", type="json", auth="none")
    def get_operating_unit(self, user, **kwargs):
        user_id = request.env["res.users"].sudo().search([("id", "=", user)], limit=1)
        print("-------------user-----------", user_id, user_id.operating_unit_ids)
        operating_unit_list = []
        if user:
            for unit in user_id.operating_unit_ids:
                if unit.id not in operating_unit_list:
                    operating_unit_list.append(unit.id)
        print("-----------operating_unit_list------------", operating_unit_list)
        return operating_unit_list
