from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    stock_location_qty = fields.Float(
        "Stock Location Qty", store=True, compute="_compute_stock_location_qty"
    )

    @api.depends("product_id")
    def _compute_stock_location_qty(self):
        for rec in self:
            location_id = (
                self.env["stock.location"]
                .sudo()
                .search(
                    [
                        (
                            "operating_unit_id",
                            "=",
                            self.env.user.default_operating_unit_id.id,
                        ),
                        ("usage", "=", "internal"),
                    ],
                    limit=1,
                    order="id asc",
                )
            )
            rec.stock_location_qty = rec.product_id.with_context(
                {"location": location_id.id,
                 "company_id": self.env.user.company_id.id}
            ).qty_available
