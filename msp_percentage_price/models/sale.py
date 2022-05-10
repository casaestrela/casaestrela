# -*- encoding: utf-8 -*-

from odoo import fields, models, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    msp_percentage = fields.Float('MSP Percentage')
    msp_subtotal = fields.Float('MSP Subtotal',compute='get_msp_subtotal')
    
    
    @api.depends('msp_percentage','price_subtotal','price_total')
    def get_msp_subtotal(self):
        for record in self:
            # record.msp_subtotal = record.price_subtotal - ((record.price_subtotal * record.msp_percentage) / 100)
            record.msp_subtotal = record.price_total - ((record.price_total * record.msp_percentage) / 100)
            
            
    
    @api.onchange('product_id')
    def product_id_change(self):
        result = super(SaleOrderLine, self).product_id_change()
        self.msp_percentage = self.product_id.msp_percentage or self.product_id.categ_id.msp_percentage
        return result
    
    
    def _prepare_invoice_line(self, **optional_values):
        res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        if self.msp_percentage:
            res['msp_percentage'] = self.msp_percentage
        if self.msp_subtotal:
            res['msp_subtotal'] = self.msp_subtotal
        return res