from functools import partial

from odoo import api, fields, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    allow_msp = fields.Boolean("Allow MSP", default=True)

    def _prepare_invoice_line(self, order_line):
        res = super(PosOrder, self)._prepare_invoice_line(order_line)
        if order_line.msp_percentage:
            res["msp_percentage"] = order_line.msp_percentage
        if order_line.msp_subtotal:
            res["msp_subtotal"] = order_line.msp_subtotal
        return res

    @api.model
    def _order_fields(self, ui_order):
        process_line = partial(
            self.env["pos.order.line"]._order_line_fields,
            session_id=ui_order["pos_session_id"],
        )

        session_id = self.env["pos.session"].browse(ui_order["pos_session_id"])

        if session_id.config_id.enable_msp is True:
            if ui_order["allow_msp"] is True:
                for line in ui_order["lines"]:
                    product_id = self.env["product.product"].browse(
                        line[2]["product_id"]
                    )
                    if product_id.msp_percentage:
                        line[2]["msp_percentage"] = product_id.msp_percentage
                    else:
                        line[2]["msp_percentage"] = product_id.categ_id.msp_percentage
        for line in ui_order["statement_ids"]:
            line[2]["cheque_date"] = ui_order["cheque_date"]
            line[2]["cheque_number"] = ui_order["cheque_number"]

        return {
            "user_id": ui_order["user_id"] or False,
            "session_id": ui_order["pos_session_id"],
            "lines": [process_line(l) for l in ui_order["lines"]]
            if ui_order["lines"]
            else False,
            "pos_reference": ui_order["name"],
            "sequence_number": ui_order["sequence_number"],
            "partner_id": ui_order["partner_id"] or False,
            "date_order": ui_order["creation_date"].replace("T", " ")[:19],
            "fiscal_position_id": ui_order["fiscal_position_id"],
            "pricelist_id": ui_order["pricelist_id"],
            "amount_paid": ui_order["amount_paid"],
            "amount_total": ui_order["amount_total"],
            "amount_tax": ui_order["amount_tax"],
            "amount_return": ui_order["amount_return"],
            "company_id": self.env["pos.session"]
            .browse(ui_order["pos_session_id"])
            .company_id.id,
            "to_invoice": ui_order["to_invoice"] if "to_invoice" in ui_order else False,
            "is_tipped": ui_order.get("is_tipped", False),
            "tip_amount": ui_order.get("tip_amount", 0),
            "allow_msp": ui_order["allow_msp"],
            "payment_ids": ui_order["statement_ids"] or False,
        }

    @api.model
    def _process_order(self, order, draft, existing_order):
        order_id = super(PosOrder, self)._process_order(order, draft, existing_order)
        if order_id:
            if order.get("data").get("statement_ids"):
                pos_order_id = self.env["pos.order"].browse(order_id)
                if pos_order_id.payment_ids:
                    for line in pos_order_id.payment_ids:
                        line.cheque_number = order.get("data").get("statement_ids")[0][
                            2
                        ]["cheque_number"]
                        line.cheque_date = order.get("data").get("statement_ids")[0][2][
                            "cheque_date"
                        ]

        return order_id


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    msp_percentage = fields.Float("MSP Percentage")
    msp_subtotal = fields.Float("MSP Subtotal", compute="_get_msp_subtotal")

    @api.depends("msp_percentage", "price_subtotal_incl")
    def _get_msp_subtotal(self):
        for record in self:
            # record.msp_subtotal = record.price_subtotal - ((record.price_subtotal * record.msp_percentage) / 100)
            record.msp_subtotal = record.price_subtotal_incl - (
                (record.price_subtotal_incl * record.msp_percentage) / 100
            )
