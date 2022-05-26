
from odoo import _, fields, models


class InventoryValuationReportWizard(models.TransientModel):
    _name = "inventory.valuation.report.wizard"
    _description = "Inventory Valuation Report Wizard"

    start_date = fields.Datetime(string="Start Date")
    end_date = fields.Datetime(string="End Date")
    company_id = fields.Many2one("res.company", string="Company")
    location = fields.Many2one(
        "stock.location", string="Location", domain="[('usage','=','internal')]"
    )

    def action_confirm_report(self):

        prev_search_id = self.env["inventory.valuation.report"].sudo().search([])
        if prev_search_id:
            prev_search_id.unlink()

        stock_move_id = (
            self.env["stock.move"]
            .sudo()
            .search(
                [
                    ("date", ">=", self.start_date),
                    ("date", "<=", self.end_date),
                    ("state", "=", "done"),
                    ("company_id", "=", self.company_id.id),
                    "|",
                    ("location_id", "=", self.location.id),
                    ("location_dest_id", "=", self.location.id),
                ],
                order="id asc",
            )
        )
        for move in stock_move_id:
            print("------------move------------------", move)
            existing_report_id = (
                self.env["inventory.valuation.report"]
                .sudo()
                .search([("name", "=", move.product_id.id)])
            )
            if existing_report_id:
                if move.picking_id:
                    if move.picking_id.picking_type_code == "internal":
                        if move.location_id == self.location:
                            existing_report_id.internal = -move.product_uom_qty
                        if move.location_dest_id == self.location:
                            existing_report_id.internal = move.product_uom_qty

                    if move.picking_id.picking_type_code == "outgoing":
                        existing_report_id.sales = move.product_uom_qty
                    if move.picking_id.picking_type_code == "incoming":
                        existing_report_id.received = move.product_uom_qty
                if move.inventory_id:
                    existing_report_id.adjustment = move.product_uom_qty
                if not move.inventory_id and not move.picking_id:
                    existing_report_id.adjustment = move.product_uom_qty
            else:
                QTY_INCOMING = move.product_id.with_context(
                    {
                        "to_date": self.start_date,
                        "location": self.location.id,
                        "company_id": self.company_id.id,
                    }
                ).incoming_qty
                QTY_OUTGOING = move.product_id.with_context(
                    {
                        "to_date": self.start_date,
                        "location": self.location.id,
                        "company_id": self.company_id.id,
                    }
                ).outgoing_qty
                BEGINNING_QTY = QTY_INCOMING - QTY_OUTGOING
                report_id = (
                    self.env["inventory.valuation.report"]
                    .sudo()
                    .create(
                        {
                            "default_code": move.product_id.default_code,
                            "name": move.product_id.id,
                            "category_id": move.product_id.categ_id.id,
                            "cost_price": move.product_id.standard_price,
                            "beginning": BEGINNING_QTY,
                            "stock_move_id": move.id,
                        }
                    )
                )
                if report_id:
                    if move.picking_id:
                        if move.picking_id.picking_type_code == "internal":
                            if move.location_id == self.location:
                                report_id.internal = -move.product_uom_qty
                            if move.location_dest_id == self.location:
                                report_id.internal = move.product_uom_qty
                        if move.picking_id.picking_type_code == "outgoing":
                            report_id.sales = move.product_uom_qty
                        if move.picking_id.picking_type_code == "incoming":
                            report_id.received = move.product_uom_qty
                    if move.inventory_id:
                        report_id.adjustment = move.product_uom_qty
                    if not move.inventory_id and not move.picking_id:
                        report_id.adjustment = move.product_uom_qty

        report_object = self.env["inventory.valuation.report"].sudo().search([])
        for report in report_object:
            if report.internal > 0:
                report.ending = (
                    report.beginning
                    - report.internal
                    + report.received
                    - report.sales
                    + report.adjustment
                )
            if report.internal < 0:
                report.ending = (
                    report.beginning
                    + report.internal
                    + report.received
                    - report.sales
                    + report.adjustment
                )
            (
                self.env["stock.valuation.layer"]
                .sudo()
                .search(
                    [
                        ("stock_move_id", "=", report.stock_move_id.id),
                        ("product_id", "=", report.name.id),
                    ],
                    limit=1,
                )
            )
            # report.valuation = report.ending * valuation_id.unit_cost
            report.valuation = report.ending * report.cost_price

        tree_view_id = self.env.ref(
            "evo_inventory_report.view_inventory_valuation_report_tree"
        )
        return {
            "name": _("Inventory Report"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "tree",
            "res_model": "inventory.valuation.report",
            "views": [(tree_view_id.id, "tree")],
            "view_id": tree_view_id.id,
            "target": "current",
        }
