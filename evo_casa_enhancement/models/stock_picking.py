from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    state = fields.Selection(selection_add=[("verified", "Verify")])
    verify_user = fields.Many2many(
        "res.users", string="Verify User", store=True
    )  # compute='compute_verify_user'
    verify_bool = fields.Boolean(string="Verify User Boolean")
    current_user_id = fields.Many2one(
        "res.users", string="User", compute="_compute_current_user"
    )

    def _compute_current_user(self):
        for rec in self:
            rec.current_user_id = self.env.user.id
            user_id = self.env.user
            user_id.check_access_rights("read")
            user_id.check_access_rule("read")

            rec.location_dest_id.operating_unit_id.check_access_rights("read")
            rec.location_dest_id.operating_unit_id.check_access_rule("read")

            rec.verify_user.check_access_rights("read")
            rec.verify_user.check_access_rule("read")

            verify_user = []
            verify_user_id = (
                self.env["res.users"]
                .sudo()
                .search(
                    [
                        (
                            "assigned_operating_unit_ids",
                            "=",
                            rec.location_dest_id.operating_unit_id.id,
                        )
                    ]
                )
            )

            for user in verify_user_id:
                user.check_access_rights("read")
                user.check_access_rule("read")
                if user.id not in verify_user:
                    verify_user.append(user.id)
            if user_id.id in verify_user:
                rec.verify_bool = True
            else:
                rec.verify_bool = False

    @api.depends("location_dest_id", "current_user_id")
    def compute_verify_user(self):
        for rec in self:
            user_id = self.env.user
            user_id.check_access_rights("read")
            user_id.check_access_rule("read")

            rec.location_dest_id.operating_unit_id.check_access_rights("read")
            rec.location_dest_id.operating_unit_id.check_access_rule("read")

            rec.verify_user.check_access_rights("read")
            rec.verify_user.check_access_rule("read")

            verify_user = []
            verify_user_id = (
                self.env["res.users"]
                .sudo()
                .search(
                    [
                        (
                            "assigned_operating_unit_ids",
                            "=",
                            rec.location_dest_id.operating_unit_id.id,
                        )
                    ]
                )
            )

            for user in verify_user_id:
                user.check_access_rights("read")
                user.check_access_rule("read")
                user.check_access_rights("write")
                user.check_access_rule("write")
                if user.id not in verify_user:
                    verify_user.append(user.id)
            if user_id.id in verify_user:
                rec.verify_bool = True
            else:
                rec.verify_bool = False

    def action_verify(self):
        for rec in self:
            rec.write({"state": "verified"})

    def action_delivery_validate(self):
        for rec in self:
            for line in rec.move_line_ids_without_package:
                line.qty_done = line.product_uom_qty
        self.button_validate()

    def button_validate(self):
        for rec in self:
            # if rec.picking_type_code == 'outgoing': for line in
            # rec.move_line_ids_without_package: if
            # line.move_id.sale_line_id: if
            # line.move_id.sale_line_id.qty_invoiced < line.qty_done: raise
            # UserError(_("Delivery Qty not more than Invoice qty"))
            if rec.picking_type_code == "internal":
                if rec.state != "verified":
                    raise UserError(_("Can Not Validate Before Verify."))

        return super(StockPicking, self).button_validate()


class StockMove(models.Model):
    _inherit = "stock.move"

    stock_location_qty = fields.Float(
        "Stock Location Qty", store=True, compute="_compute_stock_location_qty"
    )
    price_unit = fields.Float("Price Unit", store=True,
                              compute="_compute_price_unit")

    @api.depends(
        "product_id", "product_uom_qty",
        "picking_id.operating_unit_id.pricelist_id"
    )
    def _compute_price_unit(self):
        for line in self:
            product_context = dict(
                self.env.context,
                partner_id=line.picking_id.partner_id.id,
                date=line.picking_id.scheduled_date,
                uom=line.product_uom.id,
            )
            if line.product_id:
                if line.picking_id.operating_unit_id.pricelist_id:
                    (
                        price,
                        rule_id,
                    ) = line.picking_id.operating_unit_id.pricelist_id.with_context(
                        product_context
                    ).get_product_price_rule(
                        line.product_id,
                        line.product_uom_qty or 1.0,
                        line.picking_id.partner_id,
                    )
                    line.price_unit = price

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
                {"location": location_id.id, "company_id": self.env.user.company_id.id}
            ).qty_available


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _get_aggregated_product_quantities(self, **kwargs):
        """ Returns a dictionary of products (key = id+name+description+uom)
        and corresponding values of interest.

        Allows aggregation of data across separate move lines for the same
        product. This is expected to be useful in things such as delivery
        reports. Dict key is made as a combination of values we expect to
        want to group the products by (i.e. so data is not lost). This
        function purposely ignores lots/SNs because these are expected to
        already be properly grouped by line.

        returns: dictionary {product_id+name+description+uom: {product, name,
        description, qty_done, product_uom}, ...}
        """
        aggregated_move_lines = {}
        for move_line in self:
            name = move_line.product_id.display_name
            description = move_line.move_id.description_picking
            if description == name or description == move_line.product_id.name:
                description = False
            uom = move_line.product_uom_id
            line_key = (
                str(move_line.product_id.id)
                + "_"
                + name
                + (description or "")
                + "uom "
                + str(uom.id)
            )

            if line_key not in aggregated_move_lines:
                aggregated_move_lines[line_key] = {
                    "name": name,
                    "description": description,
                    "qty_done": move_line.qty_done,
                    "product_uom": uom.name,
                    "product": move_line.product_id,
                    "price_unit": move_line.move_id.sale_line_id.price_unit
                    or move_line.move_id.price_unit,
                }
            else:
                aggregated_move_lines[line_key]["qty_done"] += move_line.qty_done
                aggregated_move_lines[line_key][
                    "price_unit"
                ] += move_line.move_id.sale_line_id.price_unit
        return aggregated_move_lines
