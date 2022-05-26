from odoo import fields, models


class POSPayment(models.Model):
    _inherit = "pos.payment"

    cheque_number = fields.Char("Cheque Number")
    cheque_date = fields.Date("Cheque Date")
