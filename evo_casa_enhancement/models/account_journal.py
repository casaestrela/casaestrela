from odoo import _, api, exceptions, fields, models
from odoo.exceptions import UserError


class AccountJournal(models.Model):
    _inherit = "account.journal"

    is_cheque = fields.Boolean("Is Cheque")
