from odoo import fields, models,api,_
from datetime import datetime,timedelta,time
from dateutil.relativedelta import relativedelta
from odoo.exceptions import Warning



class SaleOrderConfirmWizard(models.TransientModel):
    _name = "sale.order.confirm.wizard"
    _description = "Sale Order Confirm Wizard"
    
    company_id = fields.Many2one('res.company', store=True,default=lambda self: self.env.company)
    payment_method_id = fields.Many2one('account.journal',string='Payment Method',domain="[('type','in',('cash','bank'))]")
    amount = fields.Monetary(currency_field='currency_id', store=True, readonly=False)
    currency_id = fields.Many2one('res.currency', string='Currency', store=True, readonly=False,compute='_compute_currency_id',help="The payment's currency.")
    payment_date = fields.Date(string="Payment Date", required=True,default=fields.Date.context_today)
    sale_order_id = fields.Many2one('sale.order',string='Sale Order')
    cheque_number = fields.Char('Cheque Number')
    cheque_date = fields.Date('Cheque Date')
    change_amount = fields.Float('Change Amount')
    is_cheque = fields.Boolean('Is Cheque')
    
    @api.onchange('payment_method_id')
    def onchange_payment_method(self):
        for rec in self:
            if rec.payment_method_id.is_cheque == True:
                rec.is_cheque = True
            else:
                rec.is_cheque = False
    
    @api.onchange('amount')
    def onchange_change_amount(self):
        for wizard in self:
            wizard.change_amount = wizard.amount - wizard.sale_order_id.amount_total
    
    @api.depends('payment_method_id')
    def _compute_currency_id(self):
        for wizard in self:
            wizard.currency_id = wizard.payment_method_id.currency_id or wizard.company_id.currency_id
            
    def action_confirm_and_pay(self):
        for wizard in self:
            wizard.sale_order_id.action_confirm()
            
            for picking in wizard.sale_order_id.picking_ids:
                picking.action_assign()
                picking.action_confirm()
                for move in picking.move_ids_without_package:
                    move.quantity_done = move.product_uom_qty
                picking.button_validate()
                
            wizard.sale_order_id._create_invoices()
            for invoice in wizard.sale_order_id.invoice_ids:
                invoice.action_post()
            ctx = {
                'active_model': 'account.move',
                'active_ids': wizard.sale_order_id.invoice_ids.ids
                }
            if wizard.amount > wizard.sale_order_id.amount_total:
                register_payments = self.env['account.payment.register'].with_context(ctx).create(
                    {
                        "payment_date": wizard.payment_date,
                        "journal_id": wizard.payment_method_id.id,
                        "payment_method_id": wizard.payment_method_id and wizard.payment_method_id.inbound_payment_method_ids and wizard.payment_method_id.inbound_payment_method_ids[0].id or False,
                        "amount":wizard.sale_order_id.amount_total,
                    }
                )
            else:
                register_payments = self.env['account.payment.register'].with_context(ctx).create(
                    {
                        "payment_date": wizard.payment_date,
                        "journal_id": wizard.payment_method_id.id,
                        "payment_method_id": wizard.payment_method_id and wizard.payment_method_id.inbound_payment_method_ids and wizard.payment_method_id.inbound_payment_method_ids[0].id or False,
                        "amount":wizard.amount,
                    }
                )
            register_payments.action_create_payments()
            for record in wizard.sale_order_id.invoice_ids:
                journal_move_id = self.env['account.move'].sudo().search([('ref','=',record.name)],limit=1)
                payment_id = self.env['account.payment'].sudo().search([('move_id','=',journal_move_id.id)],limit=1)
                payment_id.cheque_number = wizard.cheque_number
                payment_id.cheque_date = wizard.cheque_date            
    
    
    