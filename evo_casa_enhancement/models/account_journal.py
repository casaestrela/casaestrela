from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    is_cheque = fields.Boolean("Is Cheque")
