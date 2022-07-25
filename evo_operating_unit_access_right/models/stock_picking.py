from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    allow_operating_unit_ids = fields.Many2many(
        "operating.unit",
        readonly=False,
        string="Allow Operating Unit",
        store=True,
        compute="compute_allow_operating_units",
    )
    location_id = fields.Many2one(
        "stock.location",
        "Source Location",
        default=lambda self: self.env["stock.picking.type"]
        .browse(self._context.get("default_picking_type_id"))
        .default_location_src_id,
        check_company=True,
        readonly=True,
        required=True,
        domain="[('operating_unit_id', 'in',allow_operating_unit_ids)]",
        states={"draft": [("readonly", False)]},
    )

    # @api.depends('picking_type_id','location_dest_id')
    # # @api.depends('picking_type_id','picking_type_id.code','location_dest_id','location_dest_id.operating_unit_id')
    # def compute_allow_operating_units(self):
    #     warehouse_pool = self.env['stock.warehouse']
    #     for rec in self:
    #         # rec.allow_operating_unit_ids = []
    #         operating_unit_ids = []
    #         user = self.env.user
    #         rec.user_id.check_access_rights("read")
    #         rec.user_id.check_access_rule("read")
    #
    #         rec.user_id.default_operating_unit_id.check_access_rights("read")
    #         rec.user_id.default_operating_unit_id.check_access_rule("read")
    #
    #         rec.location_dest_id.operating_unit_id.check_access_rights("write")
    #         rec.location_dest_id.operating_unit_id.check_access_rule("write")
    #
    #         if rec.user_id.default_operating_unit_id:
    #         # if user.default_operating_unit_id:
    #             # operating_unit_ids.append(rec.user_id.default_operating_unit_id.id)
    #             rec.allow_operating_unit_ids = [(4,rec.user_id.default_operating_unit_id.id,0)]
    #         if rec.picking_type_id.code == 'internal':
    #             destination_loc_id = rec.location_dest_id
    #             # if destination_loc_id.operating_unit_id:
    #             #     operating_unit_ids.append(rec.location_dest_id.operating_unit_id.id)
    #             if rec.location_dest_id.operating_unit_id:
    #                 rec.allow_operating_unit_ids = [(4,rec.location_dest_id.operating_unit_id.id,0)]
    #                 # operating_unit_ids.append(rec.location_dest_id.operating_unit_id.id)
    #             if rec.location_id.operating_unit_id:
    #                 # operating_unit_ids.append(rec.location_id.operating_unit_id.id)
    #                 rec.allow_operating_unit_ids = [(4,rec.location_id.operating_unit_id.id,0)]
    #             # warehoue_ids = warehouse_pool.sudo().search([('lot_stock_id','=',destination_loc_id.id)])
    #             # for warehouse in warehoue_ids:
    #             #     if warehouse.operating_unit_id:
    #             #         operating_unit_ids.append(warehouse.operating_unit_id.id)
    #
    #         # rec.allow_operating_unit_ids = operating_unit_ids

    # @api.depends('user_id')
    # def compute_allow_operating_units(self):
    #     for rec in self:
    #         user = self.env.user
    #         for unit_id in user.operating_unit_ids:
    #             rec.allow_operating_unit_ids = [(4,unit_id.id,0)]

    @api.depends("picking_type_id", "location_dest_id")
    def compute_allow_operating_units(self):
        warehouse_pool = self.env["stock.warehouse"]
        for rec in self:
            # rec.allow_operating_unit_ids = []
            operating_unit_ids = []
            user = self.env.user
            rec.user_id.check_access_rights("read")
            rec.user_id.check_access_rule("read")

            rec.user_id.default_operating_unit_id.check_access_rights("read")
            rec.user_id.default_operating_unit_id.check_access_rule("read")

            rec.location_dest_id.operating_unit_id.check_access_rights("write")
            rec.location_dest_id.operating_unit_id.check_access_rule("write")

            if user.default_operating_unit_id:
                operating_unit_ids.append(user.default_operating_unit_id.id)
            if rec.picking_type_id.code == "internal":
                destination_loc_id = rec.location_dest_id
                if destination_loc_id.operating_unit_id:
                    operating_unit_ids.append(rec.location_dest_id.operating_unit_id.id)
                warehoue_ids = warehouse_pool.sudo().search(
                    [("lot_stock_id", "=", destination_loc_id.id)]
                )
                for warehouse in warehoue_ids:
                    if warehouse.operating_unit_id:
                        operating_unit_ids.append(warehouse.operating_unit_id.id)

            rec.allow_operating_unit_ids = operating_unit_ids
