from odoo import api, fields, models,exceptions,_
from odoo.exceptions import UserError

class POSPayment(models.Model):
    _inherit = "pos.payment"
    
    cheque_number = fields.Char('Cheque Number')
    cheque_date = fields.Date('Cheque Date')