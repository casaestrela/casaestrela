from odoo import  fields, models,api


class PosConfig(models.Model):
    _inherit = 'pos.config'
    
    operating_unit_id = fields.Many2one('operating.unit','Operating Unit')
    
   