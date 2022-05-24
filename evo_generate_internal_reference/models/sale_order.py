from odoo import models, api

class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    # @api.model
    # def create(self, vals):
    #     if vals.get('operating_unit_id'):
    #         operating_unit_id = self.env['operating.unit'].browse(vals.get('operating_unit_id'))
    #         seq_date = None
    #         if operating_unit_id:
    #             seq_data = self.env['ir.sequence'].next_by_code('sale.order', sequence_date=seq_date) or _('New')
    #             vals['name'] =seq_data + ' - %s' %(operating_unit_id.code)
    #         else:
    #             seq_data = self.env['ir.sequence'].next_by_code('sale.order', sequence_date=seq_date) or _('New')
    #             vals['name'] =seq_data
    #     result = super(SaleOrder, self).create(vals)
    #     return result