
from odoo import fields, models


class NegativeBalanceWizard(models.TransientModel):
    _name = "negative.balance.wizard"
    _description = "Negative Balance Wizard"

    account_payment_id = fields.Many2one("account.payment")

    def action_confirm_transaction(self):
        for rec in self:
            rec.account_payment_id.force_transfer = True
            rec.account_payment_id.action_post()
