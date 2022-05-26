import base64

from odoo import _, api, fields, models
from odoo.tools.misc import xlwt


class PartnerLedgerWithProduct(models.TransientModel):
    _name = "partner.ledger.with.product"
    _description = "Partner Ledger With Product"

    start_date = fields.Datetime(string="Start Date")
    end_date = fields.Datetime(string="End Date")
    company_id = fields.Many2one("res.company", string="Company")
    partner_id = fields.Many2many("res.partner")
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
    journal_id = fields.Many2many("account.account")
    excel_file_name = fields.Char("File Name")
    excel_detail_report = fields.Binary("Excel Report")

    @api.depends("user_id")
    def _compute_allow_operating_units(self):
        for rec in self:
            user = self.env.user
            for unit_id in user.operating_unit_ids:
                rec.allow_operating_unit_ids = [(4, unit_id.id, 0)]

    def action_confirm_report(self):

        workbook = xlwt.Workbook()
        self.excel_file_name = _("Partner Ledger With Product.xlsx")
        sheet = workbook.add_sheet("My Xls Report")

        search_domain = [
            ("invoice_date", ">=", self.start_date),
            ("invoice_date", "<=", self.end_date),
            ("state", "=", "posted"),
        ]

        cell_text_formate = xlwt.easyxf(
            "font:name Times New Roman; align:horiz center;",
            num_format_str="#,##0,00"
        )

        header = xlwt.easyxf(
            "font:bold True;border:left thin,right thin,top thin, bottom thin;"
            "align:horiz center;pattern: pattern solid, "
            "pattern_fore_colour gray25;"
        )

        sheet.row(0).height = 265 * 2
        sheet.col(0).width = 265 * 15
        sheet.col(1).width = 265 * 8
        sheet.col(2).width = 265 * 35
        sheet.col(3).width = 265 * 60
        sheet.col(4).width = 265 * 15
        sheet.col(5).width = 265 * 15
        sheet.col(6).width = 265 * 15

        sheet.write_merge(0, 0, 0, 0, "Partner", header)
        sheet.write_merge(0, 0, 7, 7, "Debit", header)
        sheet.write_merge(0, 0, 8, 8, "Credit", header)
        sheet.write_merge(0, 0, 9, 9, "Balance", header)

        row = 1

        jounal_domain = [("type", "in", ["sale", "purchase", "cash", "bank"])]
        journal_ids = self.env["account.journal"].search(jounal_domain)
        account_domain = [
            ("user_type_id.type", "in", ("receivable", "payable")),
            ("company_id", "=", self.env.company.id),
        ]

        accounts = self.env["account.account"].search(account_domain)
        if self.journal_id:
            account_list = []
            for account in self.journal_id:
                if account not in account_list:
                    account_list.append(account.id)
            accounts = self.env["account.account"].search([("id", "in", account_list)])

        operating_unit_list = (
            self.env["operating.unit"]
            .sudo()
            .search([("id", "in", self.env.user.assigned_operating_unit_ids.ids)])
        )
        if self.operating_unit:
            operating_unit_list = self.env["operating.unit"].search(
                [("id", "=", self.operating_unit.id)]
            )

        partner_list = []
        partner_ledger_ids = self.env["account.move.line"].search(
            [
                ("matching_number", "in", ["P", False]),
                ("move_id.journal_id", "in", journal_ids.ids),
                ("move_id.invoice_date", ">=", self.start_date),
                ("move_id.invoice_date", "<=", self.end_date),
                ("move_id.payment_state", "!=", "paid"),
            ]
        )  # ('state','=','posted'),
        payment_partner_ledger_ids = self.env["account.move.line"].search(
            [
                ("matching_number", "in", ["P", False]),
                ("move_id.date", ">=", self.start_date),
                ("move_id.date", "<=", self.end_date),
                ("move_id.payment_state", "=", False),
            ]
        )  # ('state','=','posted'),

        for ledger in partner_ledger_ids:
            if ledger.account_id in accounts:
                if ledger.partner_id not in partner_list:
                    partner_list.append(ledger.partner_id)
        for ledger in payment_partner_ledger_ids:
            if ledger.account_id in accounts:
                if ledger.partner_id not in partner_list:
                    partner_list.append(ledger.partner_id)
        if self.partner_id:
            partner_list = self.partner_id
        for partner in partner_list:
            if partner.name:
                total_partner_debit = 0.0
                total_partner_credit = 0.0
                partner_row = row
                # sheet.write_merge(row,row,0,0,str(partner.name),header)
                # sheet.write_merge(row,row,1,1,'',header)
                # sheet.write_merge(row,row,2,2,'',header)
                # sheet.write_merge(row,row,3,3,'',header)
                # sheet.write_merge(row,row,4,4,'',header)
                # sheet.write_merge(row,row,5,5,'',header)
                # sheet.write_merge(row,row,6,6,'',header)
                row += 1
                header_row = row
                # sheet.write_merge(row,row,0,0,'Date',header)
                # sheet.write_merge(row,row,1,1,'JRNL',header)
                # sheet.write_merge(row,row,2,2,'Invoice',header)
                # sheet.write_merge(row,row,3,3,'Product',header)
                # sheet.write_merge(row,row,4,4,'Quantity',header)
                # sheet.write_merge(row,row,5,5,'Unit Of Measure',header)
                # sheet.write_merge(row,row,6,6,'Unit Price',header)
                # sheet.write_merge(row,row,7,7,'Debit',header)
                # sheet.write_merge(row,row,8,8,'Credit',header)
                # sheet.write_merge(row,row,9,9,'Balance',header)

                balance = 0.0

                account_move_line_ids = (
                    self.env["account.move.line"]
                    .sudo()
                    .search(
                        [
                            ("matching_number", "=", "P"),
                            ("partner_id", "=", partner.id),
                            ("move_id.journal_id", "in", journal_ids.ids),
                        ]
                    )
                )
                not_match_account_move_line_ids = (
                    self.env["account.move.line"]
                    .sudo()
                    .search(
                        [
                            ("matching_number", "=", False),
                            ("partner_id", "=", partner.id),
                            ("move_id.journal_id", "in", journal_ids.ids),
                        ]
                    )
                )
                move_list = []
                for move_line in account_move_line_ids:
                    if move_line.move_id.id not in move_list:
                        move_list.append(move_line.move_id.id)
                for move_line in not_match_account_move_line_ids:
                    if move_line.move_id.id not in move_list:
                        move_list.append(move_line.move_id.id)

                payment_state = ["paid", False]
                account_move_ids = (
                    self.env["account.move"]
                    .sudo()
                    .search(
                        [
                            ("journal_id", "in", journal_ids.ids),
                            ("id", "in", move_list),
                            ("invoice_date", ">=", self.start_date),
                            ("invoice_date", "<=", self.end_date),
                            ("payment_state", "not in", payment_state),
                            ("state", "=", "posted"),
                        ]
                    )
                )  # ('state','=','posted'),
                account_payment_ids = (
                    self.env["account.move"]
                    .sudo()
                    .search(
                        [
                            ("journal_id", "in", journal_ids.ids),
                            ("id", "in", move_list),
                            ("date", ">=", self.start_date),
                            ("date", "<=", self.end_date),
                            ("state", "=", "posted"),
                        ]
                    )
                )  # ('state','=','posted'),

                account_move_list = []

                for move in account_move_ids:
                    if move not in account_move_list:
                        account_move_list.append(move)
                for payment in account_payment_ids:
                    if payment not in account_move_list:
                        account_move_list.append(payment)
                for move in account_move_list:
                    if move.journal_id.code != "POSS":
                        for move_line in move.line_ids:
                            if move_line.account_id in accounts:

                                if move_line.operating_unit_id in operating_unit_list:

                                    if move_line.matching_number is False:

                                        if move.invoice_date:
                                            ledger_date = move.invoice_date
                                        if move.date:
                                            ledger_date = move.date

                                        row += 1
                                        sheet.write_merge(
                                            row,
                                            row,
                                            0,
                                            0,
                                            str(ledger_date),
                                            cell_text_formate,
                                        )
                                        sheet.write_merge(
                                            row,
                                            row,
                                            1,
                                            1,
                                            str(move.journal_id.code),
                                            cell_text_formate,
                                        )
                                        sheet.write_merge(
                                            row,
                                            row,
                                            2,
                                            2,
                                            str(move.name),
                                            cell_text_formate,
                                        )
                                        sheet.write_merge(
                                            row, row, 3, 3, "", cell_text_formate
                                        )
                                        # sheet.write_merge(row,row,3,3,str(move_line.name),cell_text_formate)
                                        balance = balance + (
                                            move_line.debit - move_line.credit
                                        )
                                        total_partner_debit += move_line.debit
                                        total_partner_credit += move_line.credit
                                        sheet.write_merge(
                                            row,
                                            row,
                                            7,
                                            7,
                                            str(move_line.debit),
                                            cell_text_formate,
                                        )
                                        sheet.write_merge(
                                            row,
                                            row,
                                            8,
                                            8,
                                            str(move_line.credit),
                                            cell_text_formate,
                                        )
                                        sheet.write_merge(
                                            row,
                                            row,
                                            9,
                                            9,
                                            str(balance),
                                            cell_text_formate,
                                        )

                                        if (
                                            move.journal_id.type == "sale"
                                            or move.journal_id.type == "purchase"
                                        ):
                                            # row += 1
                                            # sheet.write_merge(row,row,2,2,'Product',header)
                                            # sheet.write_merge(row,row,3,3,'Quantity',header)
                                            # sheet.write_merge(row,row,4,4,'Price',header)
                                            # sheet.write_merge(row,row,5,5,'Total',header)

                                            for product_line in move.invoice_line_ids:
                                                row += 1
                                                # sheet.write_merge(row,row,1,1,'',cell_text_formate)
                                                sheet.write_merge(
                                                    row,
                                                    row,
                                                    3,
                                                    3,
                                                    str(product_line.name),
                                                    cell_text_formate,
                                                )
                                                sheet.write_merge(
                                                    row,
                                                    row,
                                                    4,
                                                    4,
                                                    str(product_line.quantity),
                                                    cell_text_formate,
                                                )
                                                sheet.write_merge(
                                                    row,
                                                    row,
                                                    5,
                                                    5,
                                                    str(
                                                        product_line.product_uom_id.name
                                                    ),
                                                    cell_text_formate,
                                                )
                                                sheet.write_merge(
                                                    row,
                                                    row,
                                                    6,
                                                    6,
                                                    str(product_line.price_unit),
                                                    cell_text_formate,
                                                )

                                    if move_line.matching_number == "P":

                                        if move.invoice_date:
                                            ledger_date = move.invoice_date
                                        if move.date:
                                            ledger_date = move.date

                                        row += 1
                                        sheet.write_merge(
                                            row,
                                            row,
                                            0,
                                            0,
                                            str(ledger_date),
                                            cell_text_formate,
                                        )
                                        sheet.write_merge(
                                            row,
                                            row,
                                            1,
                                            1,
                                            str(move.journal_id.code),
                                            cell_text_formate,
                                        )
                                        sheet.write_merge(
                                            row,
                                            row,
                                            2,
                                            2,
                                            str(move.name),
                                            cell_text_formate,
                                        )
                                        # sheet.write_merge(row,row,3,3,str(move_line.name),cell_text_formate)
                                        balance = balance + (
                                            move_line.debit - move_line.credit
                                        )
                                        total_partner_debit += move_line.debit
                                        total_partner_credit += move_line.credit
                                        sheet.write_merge(
                                            row,
                                            row,
                                            7,
                                            7,
                                            str(move_line.debit),
                                            cell_text_formate,
                                        )
                                        sheet.write_merge(
                                            row,
                                            row,
                                            8,
                                            8,
                                            str(move_line.credit),
                                            cell_text_formate,
                                        )
                                        sheet.write_merge(
                                            row,
                                            row,
                                            9,
                                            9,
                                            str(balance),
                                            cell_text_formate,
                                        )

                                        if (
                                            move.journal_id.type == "sale"
                                            or move.journal_id.type == "purchase"
                                        ):
                                            # row += 1
                                            # sheet.write_merge(row,row,2,2,'Product',header)
                                            # sheet.write_merge(row,row,3,3,'Quantity',header)
                                            # sheet.write_merge(row,row,4,4,'Price',header)
                                            # sheet.write_merge(row,row,5,5,'Total',header)

                                            for product_line in move.invoice_line_ids:
                                                row += 1
                                                # sheet.write_merge(row,row,1,1,'',cell_text_formate)
                                                sheet.write_merge(
                                                    row,
                                                    row,
                                                    3,
                                                    3,
                                                    str(product_line.name),
                                                    cell_text_formate,
                                                )
                                                sheet.write_merge(
                                                    row,
                                                    row,
                                                    4,
                                                    4,
                                                    str(product_line.quantity),
                                                    cell_text_formate,
                                                )
                                                sheet.write_merge(
                                                    row,
                                                    row,
                                                    5,
                                                    5,
                                                    str(
                                                        product_line.product_uom_id.name
                                                    ),
                                                    cell_text_formate,
                                                )
                                                sheet.write_merge(
                                                    row,
                                                    row,
                                                    6,
                                                    6,
                                                    str(product_line.price_unit),
                                                    cell_text_formate,
                                                )

                                if not move_line.operating_unit_id:

                                    if not move_line.matching_number:

                                        if move.invoice_date:
                                            ledger_date = move.invoice_date
                                        if move.date:
                                            ledger_date = move.date

                                        row += 1
                                        sheet.write_merge(
                                            row,
                                            row,
                                            0,
                                            0,
                                            str(ledger_date),
                                            cell_text_formate,
                                        )
                                        sheet.write_merge(
                                            row,
                                            row,
                                            1,
                                            1,
                                            str(move.journal_id.code),
                                            cell_text_formate,
                                        )
                                        sheet.write_merge(
                                            row,
                                            row,
                                            2,
                                            2,
                                            str(move.name),
                                            cell_text_formate,
                                        )
                                        # sheet.write_merge(row,row,3,3,str(move_line.name),cell_text_formate)
                                        balance = balance + (
                                            move_line.debit - move_line.credit
                                        )
                                        total_partner_debit += move_line.debit
                                        total_partner_credit += move_line.credit
                                        sheet.write_merge(
                                            row,
                                            row,
                                            7,
                                            7,
                                            str(move_line.debit),
                                            cell_text_formate,
                                        )
                                        sheet.write_merge(
                                            row,
                                            row,
                                            8,
                                            8,
                                            str(move_line.credit),
                                            cell_text_formate,
                                        )
                                        sheet.write_merge(
                                            row,
                                            row,
                                            9,
                                            9,
                                            str(balance),
                                            cell_text_formate,
                                        )

                                        if (
                                            move.journal_id.type == "sale"
                                            or move.journal_id.type == "purchase"
                                        ):
                                            # row += 1
                                            # sheet.write_merge(row,row,2,2,'Product',header)
                                            # sheet.write_merge(row,row,3,3,'Quantity',header)
                                            # sheet.write_merge(row,row,4,4,'Price',header)
                                            # sheet.write_merge(row,row,5,5,'Total',header)

                                            for product_line in move.invoice_line_ids:
                                                row += 1
                                                # sheet.write_merge(row,row,1,1,'',cell_text_formate)
                                                sheet.write_merge(
                                                    row,
                                                    row,
                                                    3,
                                                    3,
                                                    str(product_line.name),
                                                    cell_text_formate,
                                                )
                                                sheet.write_merge(
                                                    row,
                                                    row,
                                                    4,
                                                    4,
                                                    str(product_line.quantity),
                                                    cell_text_formate,
                                                )
                                                sheet.write_merge(
                                                    row,
                                                    row,
                                                    5,
                                                    5,
                                                    str(
                                                        product_line.product_uom_id.name
                                                    ),
                                                    cell_text_formate,
                                                )
                                                sheet.write_merge(
                                                    row,
                                                    row,
                                                    6,
                                                    6,
                                                    str(product_line.price_unit),
                                                    cell_text_formate,
                                                )
                                                # row += 1
                                    if move_line.matching_number == "P":

                                        if move.invoice_date:
                                            ledger_date = move.invoice_date
                                        if move.date:
                                            ledger_date = move.date

                                        row += 1
                                        sheet.write_merge(
                                            row,
                                            row,
                                            0,
                                            0,
                                            str(ledger_date),
                                            cell_text_formate,
                                        )
                                        sheet.write_merge(
                                            row,
                                            row,
                                            1,
                                            1,
                                            str(move.journal_id.code),
                                            cell_text_formate,
                                        )
                                        sheet.write_merge(
                                            row,
                                            row,
                                            2,
                                            2,
                                            str(move.name),
                                            cell_text_formate,
                                        )
                                        # sheet.write_merge(row,row,3,3,str(move_line.name),cell_text_formate)
                                        balance = balance + (
                                            move_line.debit - move_line.credit
                                        )
                                        total_partner_debit += move_line.debit
                                        total_partner_credit += move_line.credit
                                        sheet.write_merge(
                                            row,
                                            row,
                                            7,
                                            7,
                                            str(move_line.debit),
                                            cell_text_formate,
                                        )
                                        sheet.write_merge(
                                            row,
                                            row,
                                            8,
                                            8,
                                            str(move_line.credit),
                                            cell_text_formate,
                                        )
                                        sheet.write_merge(
                                            row,
                                            row,
                                            9,
                                            9,
                                            str(balance),
                                            cell_text_formate,
                                        )

                                        if (
                                            move.journal_id.type == "sale"
                                            or move.journal_id.type == "purchase"
                                        ):
                                            # row += 1
                                            # sheet.write_merge(row,row,2,2,'Product',header)
                                            # sheet.write_merge(row,row,3,3,'Quantity',header)
                                            # sheet.write_merge(row,row,4,4,'Price',header)
                                            # sheet.write_merge(row,row,5,5,'Total',header)

                                            for product_line in move.invoice_line_ids:
                                                row += 1
                                                # sheet.write_merge(row,row,1,1,'',cell_text_formate)
                                                sheet.write_merge(
                                                    row,
                                                    row,
                                                    3,
                                                    3,
                                                    str(product_line.name),
                                                    cell_text_formate,
                                                )
                                                sheet.write_merge(
                                                    row,
                                                    row,
                                                    4,
                                                    4,
                                                    str(product_line.quantity),
                                                    cell_text_formate,
                                                )
                                                sheet.write_merge(
                                                    row,
                                                    row,
                                                    5,
                                                    5,
                                                    str(
                                                        product_line.product_uom_id.name
                                                    ),
                                                    cell_text_formate,
                                                )
                                                sheet.write_merge(
                                                    row,
                                                    row,
                                                    6,
                                                    6,
                                                    str(product_line.price_unit),
                                                    cell_text_formate,
                                                )
                                                # row += 1
                if total_partner_debit or total_partner_credit:
                    sheet.write_merge(
                        partner_row, partner_row, 0, 0, str(partner.name), header
                    )
                    sheet.write_merge(partner_row, partner_row, 1, 1, "", header)
                    sheet.write_merge(partner_row, partner_row, 2, 2, "", header)
                    sheet.write_merge(partner_row, partner_row, 3, 3, "", header)
                    sheet.write_merge(partner_row, partner_row, 4, 4, "", header)
                    sheet.write_merge(partner_row, partner_row, 5, 5, "", header)
                    sheet.write_merge(partner_row, partner_row, 6, 6, "", header)
                    # row += 1
                    # header_row = row
                    sheet.write_merge(header_row, header_row, 0, 0, "Date", header)
                    sheet.write_merge(header_row, header_row, 1, 1, "JRNL", header)
                    sheet.write_merge(header_row, header_row, 2, 2, "Invoice", header)
                    sheet.write_merge(header_row, header_row, 3, 3, "Product", header)
                    sheet.write_merge(header_row, header_row, 4, 4, "Quantity", header)
                    sheet.write_merge(
                        header_row, header_row, 5, 5, "Unit Of Measure", header
                    )
                    sheet.write_merge(
                        header_row, header_row, 6, 6, "Unit Price", header
                    )
                    sheet.write_merge(header_row, header_row, 7, 7, "Debit", header)
                    sheet.write_merge(header_row, header_row, 8, 8, "Credit", header)
                    sheet.write_merge(header_row, header_row, 9, 9, "Balance", header)
                    sheet.write_merge(
                        partner_row, partner_row, 7, 7, str(total_partner_debit), header
                    )
                    sheet.write_merge(
                        partner_row,
                        partner_row,
                        8,
                        8,
                        str(total_partner_credit),
                        header,
                    )
                    sheet.write_merge(
                        partner_row,
                        partner_row,
                        9,
                        9,
                        str(total_partner_debit - total_partner_credit),
                        header,
                    )
                    # row += 1
                    row += 1

        file_name = "Partner Ledger With Product.xls"
        workbook.save(file_name)
        fp = open(file_name, "rb")
        file_data = fp.read()
        excel_file_content = base64.encodestring(file_data)
        self.excel_detail_report = excel_file_content

        action = {
            "type": "ir.actions.act_url",
            "name": "Excel Report",
            "url": "/web/content/?model=partner.ledger.with.product&field=excel_detail_report&id=%s&filename=%s&download=true"
            % (self.id, file_name),
            "target": "new",
        }
        return action

    # def action_confirm_report(self):
    #
    #     workbook = xlwt.Workbook()
    #     self.excel_file_name = _('Partner Ledger With Product.xlsx')
    #     sheet = workbook.add_sheet('My Xls Report')
    #
    #     search_domain = [('invoice_date','>=',self.start_date),('invoice_date','<=',self.end_date),('state','=','posted')]
    #
    #
    #     cell_text_formate = xlwt.easyxf('font:name Times New Roman; align:horiz center;',num_format_str='#,##0,00')
    #
    #     header = xlwt.easyxf('font:bold True;border:left thin,right thin,top thin, bottom thin;align:horiz center;pattern: pattern solid, pattern_fore_colour gray25;')
    #
    #     sheet.row(0).height = 265 * 2
    #     sheet.col(0).width = 265 * 15
    #     sheet.col(1).width = 265 * 8
    #     sheet.col(2).width = 265 * 35
    #     sheet.col(3).width = 265 * 60
    #     sheet.col(4).width = 265 * 15
    #     sheet.col(5).width = 265 * 15
    #     sheet.col(6).width = 265 * 15
    #
    #     sheet.write_merge(0,0,0,0,'Partner',header)
    #     sheet.write_merge(0,0,4,4,'Debit',header)
    #     sheet.write_merge(0,0,5,5,'Credit',header)
    #     sheet.write_merge(0,0,6,6,'Balance',header)
    #
    #
    #     row = 1
    #
    #     jounal_domain = [('type','in',['sale','purchase','cash','bank'])]
    #     journal_ids = self.env['account.journal'].search(jounal_domain)
    #     account_domain = [('user_type_id.type', 'in', ('receivable', 'payable')),
    #                       ('company_id', '=', self.env.company.id)]
    #
    #     accounts = self.env['account.account'].search(account_domain)
    #     if self.journal_id:
    #         account_list = []
    #         for account in self.journal_id:
    #             if account not in account_list:
    #                 account_list.append(account.id)
    #         accounts = self.env['account.account'].search([('id','in',account_list)])
    #
    #
    #     operating_unit_list = self.env['operating.unit'].sudo().search([('id','in',self.env.user.assigned_operating_unit_ids.ids)])
    #     if self.operating_unit:
    #         operating_unit_list = self.env['operating.unit'].search([('id','=',self.operating_unit.id)])
    #
    #     partner_list = []
    #     # partner_ledger_ids = self.env['account.move'].search([('journal_id','in',journal_ids.ids),('invoice_date','>=',self.start_date),('invoice_date','<=',self.end_date),('payment_state','!=','paid')])#('state','=','posted'),
    #     # for ledger in partner_ledger_ids:
    #     #     if ledger.line_ids:
    #     #         for line in ledger.line_ids:
    #     #             if line.account_id in accounts:
    #     #                 if ledger.partner_id not in partner_list:
    #     #                     partner_list.append(ledger.partner_id)
    #     partner_ledger_ids = self.env['account.move.line'].search([('matching_number','in',['P',False]),('move_id.journal_id','in',journal_ids.ids),('move_id.invoice_date','>=',self.start_date),('move_id.invoice_date','<=',self.end_date),('move_id.payment_state','!=','paid')])#('state','=','posted'),
    #     payment_partner_ledger_ids = self.env['account.move.line'].search([('matching_number','in',['P',False]),('move_id.date','>=',self.start_date),('move_id.date','<=',self.end_date),('move_id.payment_state','=',False)])#('state','=','posted'),
    #
    #     for ledger in partner_ledger_ids:
    #         if ledger.account_id in accounts:
    #             if ledger.partner_id not in partner_list:
    #                 partner_list.append(ledger.partner_id)
    #     for ledger in payment_partner_ledger_ids:
    #         if ledger.account_id in accounts:
    #             if ledger.partner_id not in partner_list:
    #                 partner_list.append(ledger.partner_id)
    #     if self.partner_id:
    #         partner_list = self.partner_id
    #     for partner in partner_list:
    #         if partner.name:
    #             total_partner_debit = 0.0
    #             total_partner_credit = 0.0
    #             partner_row = row
    #             sheet.write_merge(row,row,0,0,str(partner.name),header)
    #             sheet.write_merge(row,row,1,1,'',header)
    #             sheet.write_merge(row,row,2,2,'',header)
    #             sheet.write_merge(row,row,3,3,'',header)
    #             row += 1
    #             sheet.write_merge(row,row,0,0,'Date',header)
    #             sheet.write_merge(row,row,1,1,'JRNL',header)
    #             sheet.write_merge(row,row,2,2,'Move',header)
    #             sheet.write_merge(row,row,3,3,'Entry Label',header)
    #             sheet.write_merge(row,row,4,4,'Debit',header)
    #             sheet.write_merge(row,row,5,5,'Credit',header)
    #             sheet.write_merge(row,row,6,6,'Balance',header)
    #
    #             balance = 0.0
    #
    #
    #
    #             account_move_line_ids = self.env['account.move.line'].sudo().search([('matching_number','=','P'),('partner_id','=',partner.id),('move_id.journal_id','in',journal_ids.ids)])
    #             not_match_account_move_line_ids = self.env['account.move.line'].sudo().search([('matching_number','=',False),('partner_id','=',partner.id),('move_id.journal_id','in',journal_ids.ids)])
    #             move_list = []
    #             for move_line in account_move_line_ids:
    #                 if move_line.move_id.id not in move_list:
    #                     move_list.append(move_line.move_id.id)
    #             for move_line in not_match_account_move_line_ids:
    #                 if move_line.move_id.id not in move_list:
    #                     move_list.append(move_line.move_id.id)
    #
    #             payment_state = ['paid',False]
    #             account_move_ids = self.env['account.move'].sudo().search([('journal_id','in',journal_ids.ids),('id','in',move_list),('invoice_date','>=',self.start_date),('invoice_date','<=',self.end_date),('payment_state','not in',payment_state),('state','=','posted')])#('state','=','posted'),
    #             account_payment_ids = self.env['account.move'].sudo().search([('journal_id','in',journal_ids.ids),('id','in',move_list),('date','>=',self.start_date),('date','<=',self.end_date),('state','=','posted')])#('state','=','posted'),
    #
    #             account_move_list = []
    #
    #             for move in account_move_ids:
    #                 if move not in account_move_list:
    #                     account_move_list.append(move)
    #             for payment in account_payment_ids:
    #                 if payment not in account_move_list:
    #                     account_move_list.append(payment)
    #             for move in account_move_list:
    #                 for move_line in move.line_ids:
    #                     if move_line.account_id in accounts:
    #
    #                         if move_line.operating_unit_id in operating_unit_list:
    #
    #                             if move_line.matching_number == False:
    #
    #                                 if move.invoice_date:
    #                                     ledger_date = move.invoice_date
    #                                 if move.date:
    #                                     ledger_date = move.date
    #
    #                                 row += 1
    #                                 sheet.write_merge(row,row,0,0,str(ledger_date),cell_text_formate)
    #                                 sheet.write_merge(row,row,1,1,str(move.journal_id.code),cell_text_formate)
    #                                 sheet.write_merge(row,row,2,2,str(move.name),cell_text_formate)
    #                                 sheet.write_merge(row,row,3,3,str(move_line.name),cell_text_formate)
    #                                 balance = balance + (move_line.debit - move_line.credit)
    #                                 total_partner_debit += move_line.debit
    #                                 total_partner_credit += move_line.credit
    #                                 sheet.write_merge(row,row,4,4,str(move_line.debit),cell_text_formate)
    #                                 sheet.write_merge(row,row,5,5,str(move_line.credit),cell_text_formate)
    #                                 sheet.write_merge(row,row,6,6,str(balance),cell_text_formate)
    #
    #                                 if move.journal_id.type == 'sale' or move.journal_id.type == 'purchase':
    #                                     row += 1
    #                                     sheet.write_merge(row,row,2,2,'Product',header)
    #                                     sheet.write_merge(row,row,3,3,'Quantity',header)
    #                                     sheet.write_merge(row,row,4,4,'Price',header)
    #                                     sheet.write_merge(row,row,5,5,'Total',header)
    #
    #                                     for product_line in move.invoice_line_ids:
    #                                         row += 1
    #                                         sheet.write_merge(row,row,1,1,'',cell_text_formate)
    #                                         sheet.write_merge(row,row,2,2,str(product_line.name),cell_text_formate)
    #                                         sheet.write_merge(row,row,3,3,str(product_line.quantity),cell_text_formate)
    #                                         sheet.write_merge(row,row,4,4,str(product_line.price_unit),cell_text_formate)
    #                                         sheet.write_merge(row,row,5,5,str(product_line.price_total),cell_text_formate)
    #
    #                             if move_line.matching_number == 'P':
    #
    #                                 if move.invoice_date:
    #                                     ledger_date = move.invoice_date
    #                                 if move.date:
    #                                     ledger_date = move.date
    #
    #                                 row += 1
    #                                 sheet.write_merge(row,row,0,0,str(ledger_date),cell_text_formate)
    #                                 sheet.write_merge(row,row,1,1,str(move.journal_id.code),cell_text_formate)
    #                                 sheet.write_merge(row,row,2,2,str(move.name),cell_text_formate)
    #                                 sheet.write_merge(row,row,3,3,str(move_line.name),cell_text_formate)
    #                                 balance = balance + (move_line.debit - move_line.credit)
    #                                 total_partner_debit += move_line.debit
    #                                 total_partner_credit += move_line.credit
    #                                 sheet.write_merge(row,row,4,4,str(move_line.debit),cell_text_formate)
    #                                 sheet.write_merge(row,row,5,5,str(move_line.credit),cell_text_formate)
    #                                 sheet.write_merge(row,row,6,6,str(balance),cell_text_formate)
    #
    #                                 if move.journal_id.type == 'sale' or move.journal_id.type == 'purchase':
    #                                     row += 1
    #                                     sheet.write_merge(row,row,2,2,'Product',header)
    #                                     sheet.write_merge(row,row,3,3,'Quantity',header)
    #                                     sheet.write_merge(row,row,4,4,'Price',header)
    #                                     sheet.write_merge(row,row,5,5,'Total',header)
    #
    #                                     for product_line in move.invoice_line_ids:
    #                                         row += 1
    #                                         sheet.write_merge(row,row,1,1,'',cell_text_formate)
    #                                         sheet.write_merge(row,row,2,2,str(product_line.name),cell_text_formate)
    #                                         sheet.write_merge(row,row,3,3,str(product_line.quantity),cell_text_formate)
    #                                         sheet.write_merge(row,row,4,4,str(product_line.price_unit),cell_text_formate)
    #                                         sheet.write_merge(row,row,5,5,str(product_line.price_total),cell_text_formate)
    #
    #                         if not move_line.operating_unit_id:
    #
    #                             if not move_line.matching_number:
    #
    #                                 if move.invoice_date:
    #                                     ledger_date = move.invoice_date
    #                                 if move.date:
    #                                     ledger_date = move.date
    #
    #                                 row += 1
    #                                 sheet.write_merge(row,row,0,0,str(ledger_date),cell_text_formate)
    #                                 sheet.write_merge(row,row,1,1,str(move.journal_id.code),cell_text_formate)
    #                                 sheet.write_merge(row,row,2,2,str(move.name),cell_text_formate)
    #                                 sheet.write_merge(row,row,3,3,str(move_line.name),cell_text_formate)
    #                                 balance = balance + (move_line.debit - move_line.credit)
    #                                 total_partner_debit += move_line.debit
    #                                 total_partner_credit += move_line.credit
    #                                 sheet.write_merge(row,row,4,4,str(move_line.debit),cell_text_formate)
    #                                 sheet.write_merge(row,row,5,5,str(move_line.credit),cell_text_formate)
    #                                 sheet.write_merge(row,row,6,6,str(balance),cell_text_formate)
    #
    #                                 if move.journal_id.type == 'sale' or move.journal_id.type == 'purchase':
    #                                     row += 1
    #                                     sheet.write_merge(row,row,2,2,'Product',header)
    #                                     sheet.write_merge(row,row,3,3,'Quantity',header)
    #                                     sheet.write_merge(row,row,4,4,'Price',header)
    #                                     sheet.write_merge(row,row,5,5,'Total',header)
    #
    #                                     for product_line in move.invoice_line_ids:
    #                                         row += 1
    #                                         sheet.write_merge(row,row,1,1,'',cell_text_formate)
    #                                         sheet.write_merge(row,row,2,2,str(product_line.name),cell_text_formate)
    #                                         sheet.write_merge(row,row,3,3,str(product_line.quantity),cell_text_formate)
    #                                         sheet.write_merge(row,row,4,4,str(product_line.price_unit),cell_text_formate)
    #                                         sheet.write_merge(row,row,5,5,str(product_line.price_total),cell_text_formate)
    #                                         # row += 1
    #                             if move_line.matching_number == 'P':
    #
    #
    #                                 if move.invoice_date:
    #                                     ledger_date = move.invoice_date
    #                                 if move.date:
    #                                     ledger_date = move.date
    #
    #                                 row += 1
    #                                 sheet.write_merge(row,row,0,0,str(ledger_date),cell_text_formate)
    #                                 sheet.write_merge(row,row,1,1,str(move.journal_id.code),cell_text_formate)
    #                                 sheet.write_merge(row,row,2,2,str(move.name),cell_text_formate)
    #                                 sheet.write_merge(row,row,3,3,str(move_line.name),cell_text_formate)
    #                                 balance = balance + (move_line.debit - move_line.credit)
    #                                 total_partner_debit += move_line.debit
    #                                 total_partner_credit += move_line.credit
    #                                 sheet.write_merge(row,row,4,4,str(move_line.debit),cell_text_formate)
    #                                 sheet.write_merge(row,row,5,5,str(move_line.credit),cell_text_formate)
    #                                 sheet.write_merge(row,row,6,6,str(balance),cell_text_formate)
    #
    #                                 if move.journal_id.type == 'sale' or move.journal_id.type == 'purchase':
    #                                     row += 1
    #                                     sheet.write_merge(row,row,2,2,'Product',header)
    #                                     sheet.write_merge(row,row,3,3,'Quantity',header)
    #                                     sheet.write_merge(row,row,4,4,'Price',header)
    #                                     sheet.write_merge(row,row,5,5,'Total',header)
    #
    #                                     for product_line in move.invoice_line_ids:
    #                                         row += 1
    #                                         sheet.write_merge(row,row,1,1,'',cell_text_formate)
    #                                         sheet.write_merge(row,row,2,2,str(product_line.name),cell_text_formate)
    #                                         sheet.write_merge(row,row,3,3,str(product_line.quantity),cell_text_formate)
    #                                         sheet.write_merge(row,row,4,4,str(product_line.price_unit),cell_text_formate)
    #                                         sheet.write_merge(row,row,5,5,str(product_line.price_total),cell_text_formate)
    #                                         # row += 1
    #             sheet.write_merge(partner_row,partner_row,4,4,str(total_partner_debit),header)
    #             sheet.write_merge(partner_row,partner_row,5,5,str(total_partner_credit),header)
    #             sheet.write_merge(partner_row,partner_row,6,6,str(total_partner_debit - total_partner_credit),header)
    #             # row += 1
    #             row += 1
    #
    #     file_name = 'Partner Ledger With Product.xls'
    #     workbook.save(file_name)
    #     fp = open(file_name,"rb")
    #     file_data = fp.read()
    #     excel_file_content = base64.encodestring(file_data)
    #     self.excel_detail_report = excel_file_content
    #
    #     action = {
    #         'type' : 'ir.actions.act_url',
    #         'name':'Excel Report',
    #         'url': '/web/content/?model=partner.ledger.with.product&field=excel_detail_report&id=%s&filename=%s&download=true' % (self.id,file_name),
    #         'target': 'new',
    #     }
    #     return action
