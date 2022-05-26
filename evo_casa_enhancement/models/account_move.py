from odoo import _, api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    sale_return = fields.Boolean("Sale Return")
    sale_order_id = fields.Many2one("sale.order")

    def action_post(self):
        if self.move_type == "out_refund":
            sale_order_id = (
                self.env["sale.order"]
                .sudo()
                .search([("name", "=", self.invoice_origin)], limit=1)
            )
            self.sale_order_id = sale_order_id.id
            picking_id = (
                self.env["stock.picking"]
                .sudo()
                .search([("sale_id", "=", sale_order_id.id)], limit=1)
            )
            return_id = (
                self.env["stock.return.picking"]
                .sudo()
                .create(
                    {
                        "picking_id": picking_id.id,
                        "original_location_id": picking_id.location_id.id,
                        "parent_location_id": picking_id.location_dest_id.id,
                        "location_id": picking_id.location_id.id,
                    }
                )
            )

            return_id._onchange_picking_id()
            for line in self.invoice_line_ids:
                for lines in return_id.product_return_moves:
                    if line.product_id == lines.product_id:
                        lines.quantity = line.quantity

            result = return_id.create_returns()
            return_picking_id = self.env["stock.picking"].browse(result["res_id"])
            for record in return_picking_id:
                for line in self.invoice_line_ids:
                    for lines in record.move_line_ids_without_package:
                        if line.product_id == lines.product_id:
                            lines.qty_done = line.quantity
            return_picking_id.button_validate()

        return super(AccountMove, self).action_post()

    def action_sale_return(self):
        move_ids = self.env["account.move"].browse(self.id)
        self.sale_return = True
        wizard_id = (
            self.env["account.move.reversal"]
            .sudo()
            .create(
                {
                    "company_id": move_ids.company_id.id or self.env.company.id,
                    "move_ids": [(6, 0, move_ids.ids)],
                    "refund_method": (
                        len(move_ids) > 1 or move_ids.move_type == "entry"
                    )
                    and "cancel"
                    or "refund",
                }
            )
        )
        wizard_id.reverse_moves()
        move_ids = self.env["account.move"].sudo().search([], limit=1, order="id desc")
        action = {
            "name": _("Reverse Moves"),
            "type": "ir.actions.act_window",
            "res_model": "account.move",
        }
        action.update(
            {"view_mode": "form", "res_id": move_ids.id}
        )
        return action


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model
    def _default_analytic_account_id(self):
        return self.env["account.analytic.account"].search(
            [("operating_unit_ids", "=", self.env.user.default_operating_unit_id.id)],
            limit=1,
        )

    analytic_account_id = fields.Many2one(
        "account.analytic.account",
        string="Analytic Account",
        default=_default_analytic_account_id,
        index=True,
        compute="_compute_analytic_account",
        store=True,
        readonly=False,
        check_company=True,
        copy=True,
    )
    sale_order_id = fields.Many2one("sale.order")
    sale_order_line_id = fields.Many2one("sale.order.line")
    cost_price = fields.Float("Cost")
    margin = fields.Float(
        "Margin",
        compute="_compute_margin",
        digits="Product Price",
        store=True,
        groups="base.group_user",
    )
    margin_percent = fields.Float(
        "Margin (%)", compute="_compute_margin", store=True,
        groups="base.group_user"
    )
    discount_reason = fields.Many2one("reason.master", string="Discount Reason")
    discount_amount = fields.Float("Discount Amount")

    @api.depends("price_subtotal", "quantity", "cost_price")
    def _compute_margin(self):
        for line in self:
            line.margin = line.price_subtotal - (line.cost_price * line.quantity)
            line.margin_percent = (
                line.price_subtotal and line.margin / line.price_subtotal * 100
            )
