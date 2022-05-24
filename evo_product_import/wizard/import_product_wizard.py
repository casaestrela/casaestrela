import base64
import csv
import io

from odoo import fields, models


class ImportProduct(models.TransientModel):
    _name = "import.product"
    _description = "Import Product"

    product_file = fields.Binary(string="Select File", required=True)
    product_filename = fields.Char(string="Filename")

    def import_product(self):
        keys = ["sr_no", "prefix", "category_id", "name", "unit", "qty_available"]
        file_reader = []

        csv_data = base64.b64decode(self.product_file)
        data_file = io.StringIO(csv_data.decode("utf-8"))
        data_file.seek(0)
        csv_reader = csv.reader(data_file, delimiter=",")
        file_reader.extend(csv_reader)

        for i in range(len(file_reader)):
            field = list(map(str, file_reader[i]))
            values = dict(zip(keys, field))
            if values:
                if i == 0:
                    continue
                else:
                    if values["category_id"]:
                        category_id = (
                            self.env["product.category"]
                            .sudo()
                            .search([("name", "=", values["category_id"])], limit=1)
                        )
                        operating_units = self.env["operating.unit"].sudo().search([])
                        if category_id:
                            category_id.category_prefix = values["prefix"]
                        else:
                            category_id = (
                                self.env["product.category"]
                                .sudo()
                                .create(
                                    {
                                        "name": values["category_id"],
                                        "category_prefix": values["prefix"],
                                        "operating_unit_ids": [
                                            (4, unit.id) for unit in operating_units
                                        ],
                                    }
                                )
                            )
                        pos_category_id = (
                            self.env["pos.category"]
                            .sudo()
                            .search([("name", "=", values["category_id"])], limit=1)
                        )
                        if not pos_category_id:
                            pos_category_id = (
                                self.env["pos.category"]
                                .sudo()
                                .create({"name": values["category_id"],})
                            )
                        unit_category_id = (
                            self.env["uom.category"]
                            .sudo()
                            .search(
                                [("name", "=", "Custom " + values["unit"])], limit=1
                            )
                        )
                        if not unit_category_id:
                            unit_category_id = (
                                self.env["uom.category"]
                                .sudo()
                                .create({"name": "Custom " + values["unit"],})
                            )
                        unit_id = (
                            self.env["uom.uom"]
                            .sudo()
                            .search([("name", "=", values["unit"])], limit=1)
                        )
                        if not unit_id:
                            unit_id = (
                                self.env["uom.uom"]
                                .sudo()
                                .create(
                                    {
                                        "name": values["unit"],
                                        "uom_type": "reference",
                                        "active": True,
                                        "rounding": 0.01000,
                                        "category_id": unit_category_id.id,
                                    }
                                )
                            )
                        product_id = (
                            self.env["product.product"]
                            .sudo()
                            .create(
                                {
                                    "name": values["name"],
                                    "categ_id": category_id.id,
                                    "pos_categ_id": pos_category_id.id,
                                    "uom_id": unit_id.id,
                                    "uom_po_id": unit_id.id,
                                    "type": "product",
                                    "list_price": 0.0,
                                    "sale_ok": True,
                                    "purchase_ok": True,
                                    "operating_unit_ids": category_id.operating_unit_ids.ids,
                                    "available_in_pos": True,
                                    "invoice_policy": "order",
                                }
                            )
                        )
                        location_id = self.env.ref("stock.stock_location_stock")
                        inventory_id = (
                            self.env["stock.inventory"]
                            .sudo()
                            .create(
                                {
                                    "name": "Inventory " + values["name"],
                                    "location_ids": [
                                        (4, location_id.id, 0)
                                    ],  # location_id.id,
                                    "product_ids": [
                                        (4, product_id.id, 0)
                                    ],  # product_id.id,
                                    "prefill_counted_quantity": "counted",
                                }
                            )
                        )
                        inventory_id.action_start()
                        inventory_line_id = (
                            self.env["stock.inventory.line"]
                            .sudo()
                            .create(
                                {
                                    "inventory_id": inventory_id.id,
                                    "product_id": product_id.id,
                                    "location_id": location_id.id,
                                    # 'theoretical_qty':values['qty_available'],
                                    "product_qty": values["qty_available"],
                                    "product_uom_id": unit_id.id,
                                }
                            )
                        )
                        inventory_id.action_validate()
