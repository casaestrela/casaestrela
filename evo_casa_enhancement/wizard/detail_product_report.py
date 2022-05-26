# from odoo.tools.misc import xlwt
# import xlwt
import base64
import logging
from datetime import datetime
from io import BytesIO

from odoo import api, fields, models

_logger = logging.getLogger(__name__)
try:
    import xlsxwriter
except ImportError:
    _logger.debug("Can not import xlsxwriter`.")


class DetailProductReport(models.TransientModel):
    _name = "detail.product.report"
    _description = "Detail Product Report"

    company_id = fields.Many2one("res.company", string="Company")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    allow_operating_unit_ids = fields.Many2many(
        "operating.unit",
        readonly=False,
        string="Allow Operating Unit",
        store=True,
        compute="_compute_allow_operating_units",
    )
    user_id = fields.Many2one("res.users", default=lambda self: self.env.user)
    operating_unit = fields.Many2one(
        "operating.unit", domain="[('id','in',allow_operating_unit_ids)]"
    )
    product_id = fields.Many2one("product.product", string="Product")
    excel_file_name = fields.Char("File Name")
    excel_detail_report = fields.Binary("Excel Report")

    @api.depends("user_id")
    def _compute_allow_operating_units(self):
        for rec in self:
            user = self.env.user
            for unit_id in user.operating_unit_ids:
                rec.allow_operating_unit_ids = [(4, unit_id.id, 0)]

    def action_confirm_report(self):
        file_data = BytesIO()
        workbook = xlsxwriter.Workbook(file_data, {})
        sheet = workbook.add_worksheet("My Xls Report")

        header = workbook.add_format(
            {"bold": True, "valign": "center", "bg_color": "gray"}
        )
        header_1 = workbook.add_format({"bold": True, "valign": "center"})
        cell_text_formate = workbook.add_format({"bold": False, "valign": "center"})
        sheet.set_column(0, 0, 20)
        sheet.set_column(1, 1, 18)
        sheet.set_column(2, 2, 15)
        sheet.set_column(3, 3, 20)
        sheet.set_column(4, 4, 15)
        sheet.set_column(5, 5, 15)
        sheet.set_column(6, 6, 15)
        sheet.set_column(7, 7, 15)
        sheet.set_column(8, 8, 15)
        sheet.set_column(9, 9, 15)
        sheet.set_column(10, 10, 15)
        sheet.set_column(11, 11, 15)
        sheet.set_column(12, 12, 15)
        row = 0
        sheet.merge_range(row, row, 0, 4, str(self.product_id.name), header_1)
        row += 1
        sheet.write(row, 0, str(self.operating_unit.name), header_1)
        row += 1
        sheet.write(row, 0, "From Date", header_1)
        sheet.write(row, 1, str(self.start_date), header_1)
        sheet.write(row, 2, "To Date", header_1)
        sheet.write(row, 3, str(self.end_date), header_1)
        row += 1
        row += 1
        sheet.write(row, 0, "Item Register", header_1)
        row += 1
        if not self.env.user.has_group(
            "evo_casa_enhancement.group_inventory_adjustment"
        ):
            sheet.write(row, 0, "", header)
            sheet.write(row, 1, "", header)
            sheet.write(row, 2, "", header)
            sheet.write(row, 3, "", header)
            sheet.write(row, 4, "Inwards", header)
            sheet.write(row, 5, "Outwards", header)
            sheet.write(row, 6, "Closing", header)
            row += 1
            sheet.write(row, 0, "Date", header)
            sheet.write(row, 1, "Particular", header)
            sheet.write(row, 2, "Voucher Type", header)
            sheet.write(row, 3, "Voc.No.", header)
            sheet.write(row, 4, "Quantity", header)
            sheet.write(row, 5, "Quantity", header)
            sheet.write(row, 6, "Quantity", header)
            row += 1
            location_id = (
                self.env["stock.location"]
                .sudo()
                .search([("operating_unit_id", "=", self.operating_unit.id)], limit=1)
            )
            QTY_INCOMING = self.product_id.with_context(
                {"to_date": self.start_date, "location": location_id.id}
            ).incoming_qty
            QTY_OUTGOING = self.product_id.with_context(
                {"to_date": self.start_date, "location": location_id.id}
            ).outgoing_qty
            OPENING_BALANCE_QTY = QTY_INCOMING - QTY_OUTGOING
            sheet.write(row, 0, str(self.start_date), cell_text_formate)
            sheet.write(row, 1, "Opening Balance", cell_text_formate)
            sheet.write(row, 2, "", cell_text_formate)
            sheet.write(row, 3, "", cell_text_formate)
            sheet.write(row, 4, str(OPENING_BALANCE_QTY), cell_text_formate)
            sheet.write(row, 5, "", cell_text_formate)
            sheet.write(row, 6, str(OPENING_BALANCE_QTY), cell_text_formate)
            row += 1
            particular = ""
            voucher_type = ""
            voucher_no = ""
            INWARD_QTY = 0.0
            OUTWARD_QTY = 0.0
            CLOSE_QTY = 0.0
            TOTAL_INWARD_QTY = 0.0
            TOTAL_OUTWARD_QTY = 0.0
            TOTAL_CLOSE_QTY = 0.0
            product_move = (
                self.env["stock.move"]
                .sudo()
                .search(
                    [
                        ("date", ">=", self.start_date),
                        ("date", "<=", self.end_date),
                        ("product_id", "=", self.product_id.id),
                        ("state", "=", "done"),
                        ("product_uom_qty", ">", 0),
                        "|",
                        ("location_id", "=", location_id.id),
                        ("location_dest_id", "=", location_id.id),
                    ]
                )
            )  # ,('operating_unit_id','=',self.operating_unit.id)
            for product in product_move:
                product_date = datetime.strptime(
                    str(product.date), "%Y-%m-%d %H:%M:%S"
                ).date()
                if product.picking_id or product.inventory_id:
                    if product.picking_id.picking_type_code:
                        if product.picking_id.picking_type_code == "outgoing":
                            voucher_type = "Sale"
                            OUTWARD_QTY = product.product_uom_qty
                            INWARD_QTY = 0.0
                            particular = product.picking_id.partner_id.name
                        if product.picking_id.picking_type_code == "incoming":
                            voucher_type = "Purchase"
                            INWARD_QTY = product.product_uom_qty
                            OUTWARD_QTY = 0.0
                            particular = product.picking_id.partner_id.name
                        if product.picking_id.picking_type_code == "internal":
                            voucher_type = "Transfer"
                            if product.picking_id.location_id == location_id:
                                OUTWARD_QTY = product.product_uom_qty
                                INWARD_QTY = 0.0
                                particular = (
                                    product.picking_id.location_id.operating_unit_id.name
                                )
                            if product.picking_id.location_dest_id == location_id:
                                INWARD_QTY = product.product_uom_qty
                                OUTWARD_QTY = 0.0
                                particular = (
                                    product.picking_id.location_dest_id.operating_unit_id.name
                                )
                        voucher_no = product.picking_id.name

                    if product.inventory_id:
                        if product.inventory_id.location_ids in location_id:
                            voucher_type = "Journal"
                            INWARD_QTY = product.product_uom_qty
                            OUTWARD_QTY = 0.0
                            voucher_no = product.inventory_id.name
                            particular = self.operating_unit.name
                    if product.picking_id.pos_order_id:
                        voucher_type = "POS Sale"
                        for line in product.picking_id.pos_order_id.lines:
                            if line.product_id == product.product_id:
                                OUTWARD_QTY = line.qty
                                INWARD_QTY = 0.0
                    CLOSE_QTY = CLOSE_QTY + (INWARD_QTY - OUTWARD_QTY)
                    TOTAL_CLOSE_QTY += CLOSE_QTY
                    TOTAL_INWARD_QTY += INWARD_QTY
                    TOTAL_OUTWARD_QTY += OUTWARD_QTY
                    if INWARD_QTY == 0.0:
                        INWARD_QTY = ""
                    if OUTWARD_QTY == 0.0:
                        OUTWARD_QTY = ""
                    sheet.write(row, 0, str(product_date), cell_text_formate)
                    sheet.write(row, 1, str(particular), cell_text_formate)
                    sheet.write(row, 2, str(voucher_type), cell_text_formate)
                    sheet.write(row, 3, str(voucher_no), cell_text_formate)
                    sheet.write(row, 4, str(INWARD_QTY), cell_text_formate)
                    sheet.write(row, 5, str(OUTWARD_QTY), cell_text_formate)
                    sheet.write(row, 6, str(CLOSE_QTY), cell_text_formate)
                    INWARD_QTY = 0.0
                    OUTWARD_QTY = 0.0
                    row += 1
            sheet.merge_range(row, 1, row, 3, "Total", header_1)
            # sheet.write(row, 3, 'Total',header_1)
            sheet.write(row, 4, str(TOTAL_INWARD_QTY), header_1)
            sheet.write(row, 5, str(TOTAL_OUTWARD_QTY), header_1)
            sheet.write(row, 6, str(CLOSE_QTY), header_1)
        if self.env.user.has_group("evo_casa_enhancement.group_inventory_adjustment"):
            sheet.write(row, 0, "", header)
            sheet.write(row, 1, "", header)
            sheet.write(row, 2, "", header)
            sheet.write(row, 3, "", header)
            sheet.merge_range(row, 4, row, 6, "Inwards", header)
            sheet.merge_range(row, 7, row, 9, "Outwards", header)
            sheet.merge_range(row, 10, row, 12, "Closing", header)
            row += 1
            sheet.write(row, 0, "Date", header)
            sheet.write(row, 1, "Particular", header)
            sheet.write(row, 2, "Voucher", header)
            sheet.write(row, 3, "Voc.No.", header)
            sheet.write(row, 4, "Quantity", header)
            sheet.write(row, 5, "Rate", header)
            sheet.write(row, 6, "Value", header)
            sheet.write(row, 7, "Quantity", header)
            sheet.write(row, 8, "Rate", header)
            sheet.write(row, 9, "Value", header)
            sheet.write(row, 10, "Quantity", header)
            sheet.write(row, 11, "Rate", header)
            sheet.write(row, 12, "Value", header)
            row += 1
            location_id = (
                self.env["stock.location"]
                .sudo()
                .search([("operating_unit_id", "=", self.operating_unit.id)], limit=1)
            )
            QTY_INCOMING = self.product_id.with_context(
                {"to_date": self.start_date, "location": location_id.id}
            ).incoming_qty
            QTY_OUTGOING = self.product_id.with_context(
                {"to_date": self.start_date, "location": location_id.id}
            ).outgoing_qty
            OPENING_BALANCE_QTY = QTY_INCOMING - QTY_OUTGOING
            OPENING_ROW = row
            sheet.write(row, 0, str(self.start_date), cell_text_formate)
            sheet.write(row, 1, "Opening Balance", cell_text_formate)
            sheet.write(row, 2, "", cell_text_formate)
            sheet.write(row, 3, "", cell_text_formate)
            sheet.write(row, 4, str(OPENING_BALANCE_QTY), cell_text_formate)

            sheet.write(row, 7, "", cell_text_formate)
            sheet.write(row, 8, "", cell_text_formate)
            sheet.write(row, 9, "", cell_text_formate)
            sheet.write(row, 10, str(OPENING_BALANCE_QTY), cell_text_formate)

            row += 1
            particular = ""
            voucher_type = ""
            voucher_no = ""
            INWARD_QTY = 0.0
            INWARD_PRICE = 0.0
            INWARD_VALUE = 0.0
            TOTAL_INWARD = 0.0
            TOTAL_INWARD_VALUE = 0.0
            OUTWARD_QTY = 0.0
            OUTWARD_PRICE = 0.0
            OUTWARD_VALUE = 0.0
            TOTAL_OUTWARD = 0.0
            TOTAL_OUTWARD_VALUE = 0.0
            CLOSE_QTY = 0.0
            TOTAL_INWARD_QTY = 0.0
            TOTAL_OUTWARD_QTY = 0.0
            TOTAL_CLOSE_QTY = 0.0
            TOTAL_CLOSE = 0.0
            OPENING_INWARD_PRICE = 0.0
            OPENING_OUTWARD_PRICE = 0.0
            product_move = (
                self.env["stock.move"]
                .sudo()
                .search(
                    [
                        ("date", ">=", self.start_date),
                        ("date", "<=", self.end_date),
                        ("product_id", "=", self.product_id.id),
                        ("state", "=", "done"),
                        ("product_uom_qty", ">", 0),
                        "|",
                        ("location_id", "=", location_id.id),
                        ("location_dest_id", "=", location_id.id),
                    ]
                )
            )  # ,('operating_unit_id','=',self.operating_unit.id)

            for product in product_move:
                product_date = datetime.strptime(
                    str(product.date), "%Y-%m-%d %H:%M:%S"
                ).date()
                if product.picking_id or product.inventory_id:
                    if product.picking_id.picking_type_code:
                        if product.picking_id.picking_type_code == "outgoing":
                            voucher_type = "Sale"
                            OUTWARD_QTY = product.product_uom_qty
                            OUTWARD_PRICE = product.sale_line_id.price_unit
                            OUTWARD_VALUE = OUTWARD_QTY * OUTWARD_PRICE
                            if product.sale_line_id.price_unit > 0.0:
                                OPENING_OUTWARD_PRICE = product.sale_line_id.price_unit
                            INWARD_VALUE = 0.0
                            INWARD_QTY = 0.0
                            INWARD_PRICE = 0.0
                            particular = product.picking_id.partner_id.name
                        if product.picking_id.picking_type_code == "incoming":
                            voucher_type = "Purchase"
                            INWARD_QTY = product.product_uom_qty
                            INWARD_PRICE = product.purchase_line_id.price_unit
                            if product.purchase_line_id.price_unit > 0.0:
                                OPENING_INWARD_PRICE = (
                                    product.purchase_line_id.price_unit
                                )
                            INWARD_VALUE = INWARD_QTY * INWARD_PRICE
                            OUTWARD_VALUE = 0.0
                            OUTWARD_PRICE = 0.0
                            OUTWARD_QTY = 0.0
                            particular = product.picking_id.partner_id.name
                        if product.picking_id.picking_type_code == "internal":
                            voucher_type = "Transfer"
                            if product.picking_id.location_id == location_id:
                                OUTWARD_QTY = product.product_uom_qty
                                OUTWARD_PRICE = product.price_unit
                                if product.price_unit > 0.0:
                                    OPENING_OUTWARD_PRICE = product.price_unit
                                OUTWARD_VALUE = OUTWARD_QTY * OUTWARD_PRICE
                                INWARD_VALUE = 0.0
                                INWARD_QTY = 0.0
                                INWARD_PRICE = 0.0
                                particular = (
                                    product.picking_id.location_id.operating_unit_id.name
                                )
                            if product.picking_id.location_dest_id == location_id:
                                INWARD_QTY = product.product_uom_qty
                                INWARD_PRICE = product.price_unit
                                if product.price_unit > 0.0:
                                    OPENING_INWARD_PRICE = product.price_unit
                                INWARD_VALUE = INWARD_QTY * INWARD_PRICE
                                OUTWARD_PRICE = 0.0
                                OUTWARD_QTY = 0.0
                                particular = (
                                    product.picking_id.location_dest_id.operating_unit_id.name
                                )
                        voucher_no = product.picking_id.name

                    if product.inventory_id:
                        if product.inventory_id.location_ids in location_id:
                            voucher_type = "Journal"
                            INWARD_QTY = product.product_uom_qty
                            INWARD_PRICE = product.product_id.standard_price
                            INWARD_VALUE = INWARD_QTY * INWARD_PRICE
                            OPENING_INWARD_PRICE = product.product_id.standard_price
                            OUTWARD_PRICE = 0.0
                            OUTWARD_QTY = 0.0
                            OUTWARD_VALUE = 0.0
                            voucher_no = product.inventory_id.name
                            particular = self.operating_unit.name
                    if product.picking_id.pos_order_id:
                        voucher_type = "POS Sale"
                        for line in product.picking_id.pos_order_id.lines:
                            if line.product_id == product.product_id:
                                OUTWARD_QTY = line.qty
                                OUTWARD_PRICE = line.price_unit
                                OUTWARD_VALUE = OUTWARD_QTY * OUTWARD_PRICE
                                OPENING_OUTWARD_PRICE = line.price_unit
                                INWARD_VALUE = 0.0
                                INWARD_QTY = 0.0
                                INWARD_PRICE = 0.0
                    CLOSE_QTY = CLOSE_QTY + (INWARD_QTY - OUTWARD_QTY)
                    TOTAL_CLOSE_QTY += CLOSE_QTY
                    TOTAL_INWARD_QTY += INWARD_QTY
                    TOTAL_INWARD_VALUE += INWARD_VALUE
                    TOTAL_OUTWARD_QTY += OUTWARD_QTY
                    TOTAL_OUTWARD_VALUE += OUTWARD_VALUE

                    if INWARD_QTY == 0.0:
                        INWARD_QTY = ""
                    if OUTWARD_QTY == 0.0:
                        OUTWARD_QTY = ""
                    if INWARD_PRICE == 0.0:
                        INWARD_PRICE = ""
                    if OUTWARD_PRICE == 0.0:
                        OUTWARD_PRICE = ""
                    if INWARD_VALUE == 0.0:
                        INWARD_VALUE = ""
                    if OUTWARD_VALUE == 0.0:
                        OUTWARD_VALUE = ""
                    sheet.write(row, 0, str(product_date), cell_text_formate)
                    sheet.write(row, 1, str(particular), cell_text_formate)
                    sheet.write(row, 2, str(voucher_type), cell_text_formate)
                    sheet.write(row, 3, str(voucher_no), cell_text_formate)
                    sheet.write(row, 4, str(INWARD_QTY), cell_text_formate)
                    sheet.write(row, 5, str(INWARD_PRICE), cell_text_formate)
                    sheet.write(row, 6, str(INWARD_VALUE), cell_text_formate)
                    sheet.write(row, 7, str(OUTWARD_QTY), cell_text_formate)
                    sheet.write(row, 8, str(OUTWARD_PRICE), cell_text_formate)
                    sheet.write(row, 9, str(OUTWARD_VALUE), cell_text_formate)
                    sheet.write(row, 10, str(CLOSE_QTY), cell_text_formate)
                    sheet.write(row, 11, str(INWARD_PRICE), cell_text_formate)
                    sheet.write(
                        row,
                        12,
                        str(CLOSE_QTY * OPENING_INWARD_PRICE),
                        cell_text_formate,
                    )
                    INWARD_QTY = 0.0
                    OUTWARD_QTY = 0.0
                    INWARD_PRICE = 0.0
                    OUTWARD_PRICE = 0.0
                    INWARD_VALUE = 0.0
                    OUTWARD_VALUE = 0.0
                    row += 1

            TOTAL_INWARD = TOTAL_INWARD_QTY * OPENING_INWARD_PRICE
            TOTAL_OUTWARD = TOTAL_OUTWARD_QTY * OPENING_OUTWARD_PRICE
            TOTAL_CLOSE = CLOSE_QTY * OPENING_INWARD_PRICE

            sheet.write(OPENING_ROW, 5, str(OPENING_INWARD_PRICE), cell_text_formate)
            sheet.write(
                OPENING_ROW,
                6,
                str(OPENING_INWARD_PRICE * OPENING_BALANCE_QTY),
                cell_text_formate,
            )
            sheet.write(OPENING_ROW, 11, str(OPENING_INWARD_PRICE), cell_text_formate)
            sheet.write(
                OPENING_ROW,
                12,
                str(OPENING_INWARD_PRICE * OPENING_BALANCE_QTY),
                cell_text_formate,
            )

            # sheet.write(row, 3, 'Total',header_1)
            sheet.merge_range(row, 1, row, 3, "Total", header_1)
            sheet.write(row, 4, str(TOTAL_INWARD_QTY), header_1)
            sheet.write(row, 5, str(OPENING_INWARD_PRICE), header_1)
            sheet.write(row, 6, str(TOTAL_INWARD), header_1)
            sheet.write(row, 7, str(TOTAL_OUTWARD_QTY), header_1)
            sheet.write(row, 8, str(OPENING_OUTWARD_PRICE), header_1)
            sheet.write(row, 9, str(TOTAL_OUTWARD), header_1)
            sheet.write(row, 10, str(CLOSE_QTY), header_1)
            sheet.write(row, 11, str(OPENING_INWARD_PRICE), header_1)
            sheet.write(row, 12, str(TOTAL_CLOSE), header_1)

        row += 1
        workbook.close()
        file_data.seek(0)
        self.write({"excel_detail_report": base64.b64encode(file_data.getvalue())})
        file_name = "Detail Product Report.xls"
        return {
            "type": "ir.actions.act_url",
            "url": "/web/content/?model=detail.product.report&field=excel_detail_report&id=%s&filename=%s&download=true"
            % (self.id, file_name),
            "target": "self",
        }
