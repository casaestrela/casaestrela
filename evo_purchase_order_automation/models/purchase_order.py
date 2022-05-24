# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import date

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.model
    def _default_warehouse_id(self):
        warehouse_check = self.env['stock.warehouse'].search([('operating_unit_id', '=',self.env.user.default_operating_unit_id.id)],limit=1).id
        return warehouse_check

    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Warehouse',
        required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        default=_default_warehouse_id, check_company=True)

    def button_confirm(self):
        res = super(PurchaseOrder,self).button_confirm()
        for order in self:
            warehouse = order.warehouse_id
            if warehouse.is_delivery_set_to_done and order.picking_ids: 
                for picking in self.picking_ids:
                    picking.action_assign()
                    picking.action_confirm()
                    for mv in picking.move_ids_without_package:
                        mv.quantity_done = mv.product_uom_qty
                    picking.button_validate()

            if warehouse.create_invoice and not order.invoice_ids:
                order.action_create_invoice()

            if warehouse.validate_invoice and order.invoice_ids:
                for invoice in order.invoice_ids:
                    invoice.invoice_date = date.today()
                    invoice.action_post()

        return res  
