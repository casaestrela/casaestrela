from odoo import SUPERUSER_ID, api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    stock_location = fields.Many2one(
        "stock.location",
        string="Stock Location",
        store=True,
        compute="compute_stock_location_qty",
    )
    stock_location_qty = fields.Float(
        "Stock Location Qty", compute="compute_stock_location_qty"
    )
    current_user_id = fields.Many2one(
        "res.users", string="User", compute="compute_current_user"
    )

    def compute_current_user(self):
        for rec in self:
            rec.current_user_id = self.env.user.id
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
            # rec.check_access_rights("write", raise_exception=True)
            # rec.check_access_rule("write")
            rec.stock_location_qty = rec.with_context(
                {"location": location_id.id, "company_id": self.env.user.company_id.id}
            ).qty_available
            rec.stock_location = location_id.id

    @api.depends("qty_available", "responsible_id", "current_user_id")
    def compute_stock_location_qty(self):
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
            rec.stock_location_qty = rec.with_context(
                {"location": location_id.id, "company_id": self.env.user.company_id.id}
            ).qty_available
            rec.stock_location = location_id.id


class ProductProduct(models.Model):
    _inherit = "product.product"

    stock_location = fields.Many2one(
        "stock.location",
        string="Stock Location",
        store=True,
        compute="compute_stock_location_qty",
    )
    stock_location_qty = fields.Float(
        "Stock Location Qty", store=True, compute="compute_stock_location_qty"
    )
    current_user_id = fields.Many2one(
        "res.users", string="User", compute="compute_current_user"
    )

    def compute_current_user(self):
        for rec in self:
            rec.current_user_id = self.env.user.id
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
            # rec.check_access_rights("write", raise_exception=True)
            # rec.check_access_rule("write")
            rec.stock_location_qty = rec.with_context(
                {"location": location_id.id, "company_id": self.env.user.company_id.id}
            ).qty_available
            rec.stock_location = location_id.id

    @api.depends("qty_available", "responsible_id", "current_user_id")
    def compute_stock_location_qty(self):
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
            rec.stock_location_qty = rec.with_context(
                {"location": location_id.id, "company_id": self.env.user.company_id.id}
            ).qty_available
            rec.stock_location = location_id.id
