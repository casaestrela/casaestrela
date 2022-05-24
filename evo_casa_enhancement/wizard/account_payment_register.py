from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
    
    cheque_number = fields.Char('Cheque Number')
    cheque_date = fields.Date('Cheque Date')
    is_cheque = fields.Boolean('Is Cheque')
    
    @api.onchange('journal_id')
    def onchange_payment_method(self):
        for rec in self:
            if rec.journal_id.is_cheque == True:
                rec.is_cheque = True
            else:
                rec.is_cheque = False
                
    @api.depends('company_id', 'source_currency_id')
    def _compute_journal_id(self):
        user = self.env.user
        for wizard in self:
            domain = [
                ('type', 'in', ('bank', 'cash')),
                ('company_id', '=', wizard.company_id.id),
                ('operating_unit_id','in',user.assigned_operating_unit_ids.ids)
            ]
            journal = None
            if wizard.source_currency_id:
                journal = self.env['account.journal'].search(domain + [('currency_id', '=', wizard.source_currency_id.id)], limit=1)
            if not journal:
                journal = self.env['account.journal'].search(domain, limit=1)
            wizard.journal_id = journal
                
    def action_create_payments(self):
        res = super(AccountPaymentRegister,self).action_create_payments()
        
        move_list = []
        for move in self.line_ids:
            if move.move_id.id not in move_list:
                move_list.append(move.move_id.id)
        journal_move_id = self.env['account.move'].sudo().search([('id','=',move_list[0])],limit=1)
        payment_id = self.env['account.payment'].sudo().search([('ref','=',journal_move_id.payment_reference)],limit=1)
        payment_id.cheque_number = self.cheque_number
        payment_id.cheque_date = self.cheque_date  
        
        return res