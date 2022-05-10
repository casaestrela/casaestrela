from odoo import api, fields, models,exceptions,_
from odoo.exceptions import UserError

class POSPaymentMethod(models.Model):
    _inherit = "pos.payment.method"
    
    is_cheque = fields.Boolean('Is Cheque')