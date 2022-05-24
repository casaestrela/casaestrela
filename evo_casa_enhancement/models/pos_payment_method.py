from odoo import _, api, exceptions, fields, models
from odoo.exceptions import UserError


class POSPaymentMethod(models.Model):
    _inherit = "pos.payment.method"

    is_cheque = fields.Boolean("Is Cheque")
