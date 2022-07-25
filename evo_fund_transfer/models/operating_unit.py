from odoo import api, fields, models


class OperatingUnit(models.Model):
    _inherit = "operating.unit"

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
        account_id_list = []
        if account_ids:
            for rec in account_ids:
                if rec.id not in account_id_list:
                    account_id_list.append(rec.id)
        return [("id", "in", account_id_list)]

    account_id = fields.Many2one(
        "account.account", string="Account", domain=get_bank_cash_account_ids
    )
