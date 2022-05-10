from odoo import api, fields, models

class OperatingUnit(models.Model):
    _inherit = "operating.unit"
    
    pricelist_id = fields.Many2one('product.pricelist',string='Pricelist')