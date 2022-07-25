import base64
import logging
from datetime import timedelta
from io import BytesIO

from odoo import fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)


try:
    import xlsxwriter
except ImportError:
    _logger.debug("Can not import xlsxwriter`.")


class PoSPaymentReportWizard(models.TransientModel):
    _name = "pos.payment.report.wizard"
    _description = "PoS Payment Report Wizard"

    date_from = fields.Date(string="Start Date", default=fields.Date.context_today)
    date_to = fields.Date(string="End Date", default=fields.Date.context_today)
    excel_detail_report = fields.Binary("Excel Report")
    operating_unit_id = fields.Many2one(
        "operating.unit",
        string="Operating Unit",
        default=lambda self: (
            self.env["res.users"].operating_unit_default_get(self.env.uid)
        ),
    )

    def date_range(self, start, end):
        delta = end - start  # as timedelta
        days = [start + timedelta(days=i) for i in range(delta.days + 1)]
        return days

    def generate_pos_payment_report(self):
        file_data = BytesIO()
        workbook = xlsxwriter.Workbook(file_data, {})
        sheet = workbook.add_worksheet("Payment Details")

        # Excel's different formats
        bold = workbook.add_format({"bold": True, "valign": "center"})
        number_formate = workbook.add_format({"num_format": "#,##0.00"})
        bold_number_formate = workbook.add_format(
            {"bold": True, "num_format": "#,##0.00"}
        )

        # set column row width
        sheet.set_column(0, 10, 15)

        # File Content
        tital_name = (
            "Payment Report : "
            + self.date_from.strftime("%d-%b-%Y")
            + " to "
            + self.date_to.strftime("%d-%b-%Y")
        )
        dates = self.date_range(self.date_from, self.date_to)

        pos_payment_methods_ids = self.env["pos.payment.method"].search([])
        account_journal_ids = self.env["account.journal"].search(
            [("type", "in", ("bank", "cash"))]
        )
        sheet.merge_range(
            0,
            0,
            0,
            1 + len(pos_payment_methods_ids) + len(account_journal_ids) or 5,
            tital_name or "",
            bold,
        )

        row = 2
        col = 0

        sheet.write(row, col, "Date", bold)
        col = 1
        for payment_method_id in pos_payment_methods_ids:
            sheet.write(row, col, "PoS : %s" % (payment_method_id.name or ""), bold)
            col += 1
        for account_journal_id in account_journal_ids:
            sheet.write(row, col, account_journal_id.name or "", bold)
            col += 1
        sheet.write(row, col, "Total", bold)

        payment_dic = {}
        for payment_method_id in pos_payment_methods_ids:
            for date in dates:
                total_amount = 0.0
                pos_payment_ids = self.env["pos.payment"].search(
                    [
                        ("payment_date", ">=", date.strftime("%Y-%m-%d 00:00:00")),
                        ("payment_date", "<=", date.strftime("%Y-%m-%d 23:59:59")),
                        ("payment_method_id", "=", payment_method_id.id),
                        (
                            "pos_order_id.operating_unit_id",
                            "=",
                            self.operating_unit_id.id,
                        ),
                    ]
                )
                for pos_payment_id in pos_payment_ids:
                    total_amount += pos_payment_id.amount

                if date in payment_dic:
                    payment_dic[date].update({payment_method_id: total_amount})
                else:
                    payment_dic.update({date: {payment_method_id: total_amount}})

        for account_journal_id in account_journal_ids:
            for date in dates:
                total_amount = 0.0
                account_payment_ids = self.env["account.payment"].search(
                    [
                        ("date", ">=", date.strftime("%Y-%m-%d")),
                        ("date", "<=", date.strftime("%Y-%m-%d")),
                        ("journal_id", "=", account_journal_id.id),
                        ("operating_unit_id", "=", self.operating_unit_id.id),
                    ]
                )

                for account_payment_id in account_payment_ids:
                    total_amount += account_payment_id.amount

                if date in payment_dic:
                    payment_dic[date].update({account_journal_id: total_amount})
                else:
                    payment_dic.update({date: {account_journal_id: total_amount}})

        row += 1
        col = 0
        payment_amount_dic = {}
        for date, type_data in payment_dic.items():
            sheet.write(row, col, date.strftime("%d-%m-%Y") or "")
            col += 1
            total_pos_row_amount = 0.0
            for payment_method_id in pos_payment_methods_ids:
                sheet.write(row, col, type_data[payment_method_id], number_formate)
                total_pos_row_amount += type_data[payment_method_id]
                if payment_method_id in payment_amount_dic:
                    payment_amount_dic[payment_method_id] += type_data[
                        payment_method_id
                    ]
                else:
                    payment_amount_dic.update(
                        {payment_method_id: type_data[payment_method_id]}
                    )
                col += 1
            total_journal_row_amount = 0.0
            for account_journal_id in account_journal_ids:
                sheet.write(row, col, type_data[account_journal_id], number_formate)
                total_journal_row_amount += type_data[account_journal_id]
                if account_journal_id in payment_amount_dic:
                    payment_amount_dic[account_journal_id] += type_data[
                        account_journal_id
                    ]
                else:
                    payment_amount_dic.update(
                        {account_journal_id: type_data[account_journal_id]}
                    )
                col += 1
            sheet.write(
                row,
                col,
                total_pos_row_amount + total_journal_row_amount,
                bold_number_formate,
            )

            if "amount" in payment_amount_dic:
                payment_amount_dic["amount"] += (
                    total_pos_row_amount + total_journal_row_amount
                )
            else:
                payment_amount_dic.update(
                    {"amount": total_pos_row_amount + total_journal_row_amount}
                )

            row += 1
            col = 0

        col = 0
        sheet.write(row, col, "TOTAL", bold)

        col = 1
        for payment_method_id in pos_payment_methods_ids:
            sheet.write(
                row, col, payment_amount_dic[payment_method_id], bold_number_formate
            )
            col += 1
        for account_journal_id in account_journal_ids:
            sheet.write(
                row, col, payment_amount_dic[account_journal_id], bold_number_formate
            )
            col += 1

        sheet.write(row, col, payment_amount_dic["amount"], bold_number_formate)

        # File Close and Write in Odoo
        workbook.close()
        file_data.seek(0)
        self.write({"excel_detail_report": base64.b64encode(file_data.getvalue())})
        file_name = "Payments Report.xls"
        return {
            "type": "ir.actions.act_url",
            "url": "/web/content/?model=pos.payment.report.wizard&field=excel_detail_report&id=%s&filename=%s&download=true"
            % (self.id, file_name),
            "target": "self",
        }
