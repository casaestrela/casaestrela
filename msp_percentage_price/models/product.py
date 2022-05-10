# -*- encoding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    msp_percentage = fields.Float('MSP Percentage')
    
    @api.constrains('msp_percentage')
    def check_msp_percentage(self):
        """ Make sure that MSP percentage is between 0 to 100 """
        for record in self:
            if record.msp_percentage < 0:
                raise UserError(_("MSP percentage not to be negative"))
            if record.msp_percentage > 100:
                raise UserError(_("MSP percentage not more than 100"))