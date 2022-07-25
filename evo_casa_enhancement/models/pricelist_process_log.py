from odoo import _, api, fields, models


class ProcessLog(models.Model):
    _name = "pricelist.process.log"
    _order = "process_date desc"
    _description = "Pricelist Process Log"

    process_date = fields.Date(
        "Date",
        default=lambda self: self._context.get("date", fields.Date.context_today(self)),
    )
    pricelist_id = fields.Many2one("product.pricelist", string="Price List")
    total_processed_record = fields.Integer("Processed Successfully")
    total_unprocessed_record = fields.Integer("Total Failure")
    total_records = fields.Integer("Total")
    processed_log_details_ids = fields.One2many(
        "pricelist.process.detail.log", "process_log_id", string="Error Details"
    )


class ProcessDetailLog(models.Model):
    _name = "pricelist.process.detail.log"
    _description = "pricelist.process.detail.log"

    process_log_id = fields.Many2one("pricelist.process.log", string="Process Log")
    file_row_number = fields.Integer("Row Number")
    file_product_default_code = fields.Char("SLC Code")
    file_process_error = fields.Text("Error")
