from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _payment_total(self):
        for rec in self:
            if rec.invoice_ids:
                total_inv_payment = 0
                for inv in rec.invoice_ids:
                    inv_payment = self.env["advance.payment.line"].search(
                        [("invoice_id", "=", inv.id),
                         ("invoice_id", "!=", False)]
                    )
                    for pay_line in inv_payment:
                        total_inv_payment += pay_line.reconcile_amount
                rec.total_sale_payment = total_inv_payment
            else:
                rec.total_sale_payment = 0.0

    total_sale_payment = fields.Monetary(
        string="Total Invoiced", compute="_payment_total"
    )

    def action_view_sale_payment(self):
        self.ensure_one()
        payment_ids = []
        action = self.env["ir.actions.actions"]._for_xml_id(
            "account.action_account_payments"
        )
        if self.invoice_ids:
            for inv in self.invoice_ids:
                inv_payment = self.env["advance.payment.line"].search(
                    [("invoice_id", "=", inv.id), ("invoice_id", "!=", False)]
                )
                for pay_line in inv_payment:
                    payment_ids.append(pay_line.payment_id.id)
        action["domain"] = [("id", "in", payment_ids)]
        return action
