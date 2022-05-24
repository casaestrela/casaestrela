from odoo import _, api, exceptions, fields, models
from odoo.exceptions import UserError


class FundTransferMaster(models.Model):
    _name = "fund.transfer.master"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Fund Transfer Master"
    _rec_name = "name"

    def default_get_from_account_id(self):
        op_unit_id = self.env["res.users"].operating_unit_default_get(self.env.uid)
        if op_unit_id.account_id:
            return op_unit_id.account_id.id

    def get_bank_cash_account_ids(self):
        bank_cash_type_id = (
            self.env["account.account.type"]
            .sudo()
            .search([("name", "=", "Bank and Cash")], limit=1)
        )
        account_ids = (
            self.env["account.account"]
            .sudo()
            .search([("user_type_id", "=", bank_cash_type_id.id)])
        )
        op_unit_id = self.env["res.users"].operating_unit_default_get(self.env.uid)
        account_id_list = []
        if account_ids:
            for rec in account_ids:
                operat_id = (
                    self.env["operating.unit"]
                    .sudo()
                    .search([("account_id", "=", rec.id)])
                )
                if (
                    operat_id
                    and rec.id not in account_id_list
                    and op_unit_id.account_id.id != rec.id
                ):
                    account_id_list.append(rec.id)
        return [("id", "in", account_id_list)]

    # def get_operating_unit_ids(self):
    #     company_id = self.env.company
    #     user_op_unit_id = self.env["res.users"].operating_unit_default_get(self.env.uid)
    #     operating_unit_ids = self.env['operating.unit'].sudo().search([('id', '!=', user_op_unit_id.id),('company_id', '=', company_id.id)])
    #     print("operating_unit_ids--------------", operating_unit_ids)
    #     operating_unit_id_list = []
    #     if operating_unit_ids:
    #         for rec in operating_unit_ids:
    #             if rec.id not in operating_unit_id_list:
    #                 operating_unit_id_list.append(rec.id)
    #     print("operating_unit_id_list---------------", operating_unit_id_list)
    #     return [('id', 'in', operating_unit_id_list)]

    def _get_default_jouranl(self):
        mis_journal_id = self.env["account.journal"].search(
            [("type", "=", "general")], limit=1
        )
        return mis_journal_id.id

    name = fields.Char("Name", copy=False,)
    journal_id = fields.Many2one(
        "account.journal",
        string="Journal",
        copy=False,
        states={"draft": [("readonly", False)]},
        check_company=True,
        default=_get_default_jouranl,
    )
    company_id = fields.Many2one(
        "res.company", store=True, readonly=True, default=lambda self: self.env.company
    )
    move_id = fields.Many2one(
        "account.move",
        string="Journal Entry",
        copy=False,
        ondelete="cascade",
        check_company=True,
    )
    operating_unit_id = fields.Many2one(
        "operating.unit",
        string="From Operating Unit",
        default=lambda self: (
            self.env["res.users"].operating_unit_default_get(self.env.uid)
        ),
    )
    to_operating_unit_id = fields.Many2one("operating.unit", string="To Operating Unit")
    from_account_id = fields.Many2one(
        "account.account",
        string="From Account",
        copy=False,
        default=default_get_from_account_id,
    )
    to_account_id = fields.Many2one(
        "account.account",
        string="To Account",
        copy=False,
        domain=get_bank_cash_account_ids,
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("verified", "Verified"),
            ("posted", "Posted"),
        ],
        string="Status",
        required=True,
        readonly=True,
        copy=False,
        default="draft",
        tracking=True,
    )
    payment_type_selection = fields.Selection(
        selection=[("cash", "Cash"), ("dd_cheque", "Cheque/DD"), ("bank", "Bank")],
        string="Payment Option",
    )
    dd_cheque_no = fields.Char(string="DD/Cheque no.", copy=False)
    dd_cheque_date = fields.Date(string="DD/Cheque Date", copy=False)
    date = fields.Date(
        string="Transaction Date",
        states={"draft": [("readonly", False)]},
        copy=False,
        default=fields.Date.context_today,
    )
    subtotal = fields.Float("Subtotal", default=0.0)
    reject_lines = fields.One2many(
        "fund.transfer.reject.reason", "transfer_id", string="Reject Lines", copy=False
    )
    is_reject_line = fields.Boolean(string="Is Reject", copy=False)
    verified_by = fields.Many2one("res.users", string="Verified by", copy=False)
    validate_by = fields.Many2one("res.users", string="Validate by", copy=False)

    def action_submitted(self):
        if self.subtotal == 0.0:
            raise UserError(_("You can't submit if subtotal is 0.0"))
        self.state = "submitted"

    def action_verified(self):
        operating_unit_id = self.env["res.users"].operating_unit_default_get(
            self.env.uid
        )
        if self.to_operating_unit_id.id != operating_unit_id.id:
            raise UserError(
                _("Only 'To Operating Unit' user can verified the fund transfer.")
            )

        if self.move_id:
            line_list = []
            line_list.append(
                {
                    "debit": self.subtotal,
                    "account_id": self.to_account_id.id,
                    "move_id": self.move_id.id,
                    "operating_unit_id": self.to_operating_unit_id.id,
                }
            )
            line_list.append(
                {
                    "credit": self.subtotal,
                    "account_id": self.from_account_id.id,
                    "move_id": self.move_id.id,
                    "operating_unit_id": self.operating_unit_id.id,
                }
            )

            move_line_ids = self.env["account.move.line"].create(line_list)
            self.move_id.write({"line_ids": [(6, 0, move_line_ids.ids)]})
        else:
            line_list = []
            line_list.append(
                (
                    0,
                    0,
                    {
                        "debit": self.subtotal,
                        "account_id": self.to_account_id.id,
                        "operating_unit_id": self.to_operating_unit_id.id,
                    },
                )
            )
            line_list.append(
                (
                    0,
                    0,
                    {
                        "credit": self.subtotal,
                        "account_id": self.from_account_id.id,
                        "operating_unit_id": self.operating_unit_id.id,
                    },
                )
            )

            vals = {"ref": "%s" % (self.name), "line_ids": line_list}
            account_move_id = self.env["account.move"].create(vals)
            self.move_id = account_move_id.id
        self.move_id.write({"operating_unit_id": self.operating_unit_id.id})
        self.state = "verified"
        self.verified_by = self._uid

    def action_validate(self):
        operating_unit_id = self.env["res.users"].operating_unit_default_get(
            self.env.uid
        )
        if self.operating_unit_id.id != operating_unit_id.id:
            raise UserError(
                _("Only 'From Operating Unit' user can validate the fund transfer.")
            )
        self.move_id.sudo().post()
        self.state = "posted"
        self.validate_by = self._uid
        return

    def action_reset_to_draft(self):
        return {
            "name": _("Reject Reason"),
            "type": "ir.actions.act_window",
            "res_model": "reject.reason",
            "view_mode": "form",
            "target": "new",
            "context": {"default_transfer_id": self.id,},
        }

    @api.onchange("to_account_id")
    def _onchange_to_account_id(self):
        if self.to_account_id:
            operat_id = (
                self.env["operating.unit"]
                .sudo()
                .search([("account_id", "=", self.to_account_id.id)], limit=1)
            )
            if operat_id:
                self.to_operating_unit_id = operat_id.id
            else:
                self.to_operating_unit_id = False
        else:
            self.to_account_id = False


class FundTransferRejectReason(models.Model):
    _name = "fund.transfer.reject.reason"
    _description = "Fund Transfer Reject Reason"
    _rec_name = "transfer_id"

    transfer_id = fields.Many2one("fund.transfer.master", string="Transfer")
    reject_date = fields.Date(string="Date")
    user_id = fields.Many2one("res.users", string="User")
    reject_reason = fields.Text(string="Reason")


class RejectReasonWizard(models.TransientModel):
    _name = "reject.reason"
    _description = "Fund Reject Reason"

    transfer_id = fields.Many2one("fund.transfer.master", string="Transfer")
    reject_reason = fields.Text(string="Reason")

    def reject_transfer(self):
        reject_val = {
            "transfer_id": self.transfer_id.id,
            "user_id": self._uid,
            "reject_date": fields.Date.context_today(self),
            "reject_reason": self.reject_reason,
        }
        reject_if = self.env["fund.transfer.reject.reason"].create(reject_val)
        self.transfer_id.write({"state": "draft", "is_reject_line": True})
