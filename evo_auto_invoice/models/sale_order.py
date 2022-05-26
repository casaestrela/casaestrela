from odoo import _, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm_wo_pay(self):
        # for line in self.order_line: product_context = dict(
        # self.env.context, partner_id=self.partner_id.id,
        # date=self.date_order, uom=line.product_uom.id) price, rule_id =
        # self.pricelist_id.with_context(
        # product_context).get_product_price_rule(line.product_id,
        # line.product_uom_qty or 1.0, self.partner_id) if price >
        # line.price_unit: raise UserError(_("Price cannot be lower then
        # price list"))

        for rec in self:
            rec.action_confirm()

            for picking in rec.picking_ids:
                picking.action_assign()
                picking.action_confirm()
                for move in picking.move_ids_without_package:
                    move.quantity_done = move.product_uom_qty
                picking.button_validate()

            rec._create_invoices()
            for invoice in rec.invoice_ids:
                invoice.action_post()

    def action_confirm_pay(self):
        # for line in self.order_line: product_context = dict(
        # self.env.context, partner_id=self.partner_id.id,
        # date=self.date_order, uom=line.product_uom.id) price, rule_id =
        # self.pricelist_id.with_context(
        # product_context).get_product_price_rule(line.product_id,
        # line.product_uom_qty or 1.0, self.partner_id) if price >
        # line.price_unit: raise UserError(_("Price cannot be lower then
        # price list"))
        wizard_id = (
            self.env["sale.order.confirm.wizard"]
            .sudo()
            .create({"sale_order_id": self.id, "amount": self.amount_total})
        )
        form_view_id = self.env.ref("evo_auto_invoice.view_sale_order_confirm_wizard")
        return {
            "name": _("Confirm"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "sale.order.confirm.wizard",
            "res_id": wizard_id.id,
            "views": [(form_view_id.id, "form")],
            "view_id": form_view_id.id,
            "target": "new",
        }
