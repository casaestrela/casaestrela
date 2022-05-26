from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        for rec in self:
            for line in rec.order_line:
                if line.price_subtotal < line.discount_amount:
                    raise UserError(_("Can Not Add Discount More Than Sale Price"))
        return super(SaleOrder, self).action_confirm()

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals["sale_order_id"]: self.id
        return invoice_vals


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    discount_reason = fields.Many2one("reason.master", string="Discount Reason")
    discount_amount = fields.Float("Discount Amount")
    invoice_id = fields.Many2one(
        "account.move",
        string="Invoice Reference",
        store=True,
        compute="_compute_invoice_id",
    )

    @api.depends("order_id.invoice_ids")
    def _compute_invoice_id(self):
        for rec in self:
            if rec.order_id.invoice_ids:
                rec.invoice_id = rec.order_id.invoice_ids[0].id

    def _prepare_invoice_line(self, **optional_values):
        res = super(SaleOrderLine, self)._prepare_invoice_line()
        res.update(
            {
                "sale_order_id": self.order_id.id,
                "sale_order_line_id": self.id,
                "cost_price": self.purchase_price,
                "discount_reason": self.discount_reason,
                "discount_amount": self.discount_amount,
                # 'margin': self.margin,
                # 'margin_percent':self.margin_percent,
            }
        )
        return res

    @api.depends(
        "product_uom_qty", "discount", "price_unit", "tax_id", "discount_amount"
    )
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(
                price,
                line.order_id.currency_id,
                line.product_uom_qty,
                product=line.product_id,
                partner=line.order_id.partner_shipping_id,
            )
            line.update(
                {
                    "price_tax": sum(
                        t.get("amount", 0.0) for t in taxes.get("taxes", [])
                    ),
                    "price_total": taxes["total_included"],
                    "price_subtotal": taxes["total_excluded"],
                }
            )
            if self.env.context.get(
                "import_file", False
            ) and not self.env.user.user_has_groups("account.group_account_manager"):
                line.tax_id.invalidate_cache(
                    ["invoice_repartition_line_ids"], [line.tax_id.id]
                )

    # @api.onchange('discount','price_unit') def onchange_discount(self): for
    # rec in self: rec.discount_amount = (( rec.price_unit *
    # rec.product_uom_qty) * rec.discount ) / 100

    @api.onchange("discount_amount", "price_unit", "product_uom_qty")
    def onchange_discount_amount(self):
        for rec in self:
            # rec.discount = ((rec.price_unit * rec.product_uom_qty) * (
            # rec.discount_amount / 100))/100
            if rec.discount_amount:
                rec.discount = (rec.discount_amount * 100) / (
                    rec.price_unit * rec.product_uom_qty
                )
            if rec.discount_amount == 0.0:
                rec.discount = 0.0
