from odoo import api, fields, models


class POSConfig(models.Model):
    _inherit = "pos.config"

    enable_msp = fields.Boolean("Active Sale Commission")
