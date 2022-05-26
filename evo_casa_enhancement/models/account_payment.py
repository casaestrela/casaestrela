from datetime import date

from odoo import _, fields, models
from odoo.exceptions import UserError


class Payment(models.Model):
    _inherit = "account.payment"

    force_transfer = fields.Boolean("Force Transfer")

    def action_post(self):
        allow_back_date = self.env.user.has_group(
            "evo_casa_enhancement.group_back_date_transaction"
        )
        if allow_back_date is False:
            if self.date < date.today():
                raise UserError(_("You Can Not Allow Back Dated Transactions"))

        if self.payment_type == "outbound":
            debit_total = 0.0
            credit_total = 0.0
            balance = 0.0
            if self.journal_id:
                debit_id = (
                    self.env["account.payment"]
                    .sudo()
                    .search(
                        [
                            ("journal_id", "=", self.journal_id.id),
                            ("payment_type", "=", "outbound"),
                        ]
                    )
                )
                for debit in debit_id:
                    debit_total += debit.amount
                credit_id = (
                    self.env["account.payment"]
                    .sudo()
                    .search(
                        [
                            ("journal_id", "=", self.journal_id.id),
                            ("payment_type", "=", "outbound"),
                        ]
                    )
                )
                for credit in credit_id:
                    credit_total += credit.amount
            balance = credit_total - debit_total
            if self.amount > balance:
                if self.force_transfer is False:
                    wizard_id = (
                        self.env["negative.balance.wizard"]
                        .sudo()
                        .create({"account_payment_id": self.id})
                    )
                    return {
                        "name": _("Negative Balance"),
                        "type": "ir.actions.act_window",
                        "view_type": "form",
                        "view_mode": "form",
                        "res_model": "negative.balance.wizard",
                        "res_id": wizard_id.id,
                        "target": "new",
                    }
        return super(Payment, self).action_post()
