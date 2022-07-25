import base64
from datetime import datetime, timedelta
from io import BytesIO

from dateutil.relativedelta import relativedelta

from odoo import _, fields, models
from odoo.exceptions import Warning
from odoo.tools.misc import xlwt


class MSPReportWizard(models.TransientModel):
    _name = "msp.report.wizard"
    _description = "Resumo Report Wizard"

    start_date = fields.Datetime(string="Start Date")
    end_date = fields.Datetime(string="End Date")
    excel_detail_report = fields.Binary("Excel Report")
    operating_unit_id = fields.Many2one(
        "operating.unit",
        string="Operating Unit",
        default=lambda self: (
            self.env["res.users"].operating_unit_default_get(self.env.uid)
        ),
    )
    excel_file_name = fields.Char("Expiry Report.xls")

    def action_generate_report(self):

        workbook = xlwt.Workbook()
        self.excel_file_name = _("Resumo Report.xlsx")
        sheet = workbook.add_sheet("My Xls Report")

        cell_text_formate = xlwt.easyxf(
            "font:name Times New Roman; align:horiz center;", num_format_str="#,##0,00"
        )

        header = xlwt.easyxf(
            "font:bold True;border:left thin,right thin,top thin, bottom thin;align:horiz center;"
        )

        sheet.row(0).height = 265 * 2
        sheet.col(0).width = 265 * 15
        sheet.col(1).width = 265 * 35
        sheet.col(2).width = 265 * 20

        sheet.write_merge(0, 0, 0, 0, "Invoice Date", header)
        sheet.write_merge(0, 0, 1, 1, "Invoice Number", header)
        sheet.write_merge(0, 0, 2, 2, "Total MSP", header)

        row = 1
        total = 0.0
        invoice_ids = (
            self.env["account.move"]
            .sudo()
            .search(
                [
                    ("move_type", "=", "out_invoice"),
                    ("state", "=", "posted"),
                    ("operating_unit_id", "=", self.operating_unit_id.id),
                ],
                order="invoice_date asc",
            )
        )  # ('payment_state', '=', 'paid'),
        for invoice in invoice_ids:

            invoice_date = invoice.invoice_date.strftime("%d/%m/%Y")
            sheet.write_merge(row, row, 0, 0, str(invoice_date), cell_text_formate)
            sheet.write_merge(row, row, 1, 1, str(invoice.name), cell_text_formate)
            total_msp = 0.0
            for line in invoice.invoice_line_ids:
                total_msp += line.msp_subtotal
                total += line.msp_subtotal
            # sheet.write_merge(row,row,2,2,str(total_msp),cell_text_formate)
            sheet.write_merge(
                row, row, 2, 2, str(round(total_msp, 2)), cell_text_formate
            )
            row += 1
        sheet.write_merge(row, row, 0, 0, "Total", header)
        sheet.write_merge(row, row, 1, 1, "", header)
        sheet.write_merge(row, row, 2, 2, str(total), header)

        file_name = "Resumo Report.xls"
        workbook.save(file_name)
        fp = open(file_name, "rb")
        file_data = fp.read()
        excel_file_content = base64.encodestring(file_data)
        self.excel_detail_report = excel_file_content

        action = {
            "type": "ir.actions.act_url",
            "name": "Excel Report",
            "url": "/web/content/?model=msp.report.wizard&field=excel_detail_report&id=%s&filename=%s&download=true"
            % (self.id, file_name),
            "target": "new",
        }
        return action
