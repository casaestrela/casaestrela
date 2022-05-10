from odoo import models, fields, api


class POSConfig(models.Model):
    _inherit = 'pos.config'

    enable_msp = fields.Boolean('Active Sale Commission')