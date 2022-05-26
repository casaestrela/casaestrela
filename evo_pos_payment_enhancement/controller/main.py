from odoo import http
from odoo.http import request


class UpdateChequeDetail(http.Controller):
    @http.route("/update_cheque_detail", type="json", auth="none")
    def update_cheque_detail(self, order_ref, cheque_number, cheque_date, **kwargs):

        order_id = (
            request.env["pos.order"]
            .sudo()
            .search([("pos_reference", "=", order_ref)], limit=1)
        )
        if order_id.payment_ids:
            for line in order_id.payment_ids:
                line.cheque_number = cheque_number
                line.cheque_date = cheque_date

            return True
