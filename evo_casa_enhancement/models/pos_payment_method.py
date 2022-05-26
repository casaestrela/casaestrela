from odoo import fields, models


class POSPaymentMethod(models.Model):
    _inherit = "pos.payment.method"

    is_cheque = fields.Boolean("Is Cheque")
