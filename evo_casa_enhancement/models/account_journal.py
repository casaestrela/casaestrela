from odoo import api, fields, models,exceptions,_
from odoo.exceptions import UserError

class AccountJournal(models.Model):
    _inherit = "account.journal"
    
    is_cheque = fields.Boolean('Is Cheque')