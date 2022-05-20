from odoo import api, fields, models,exceptions,_
from odoo.exceptions import UserError

class HRExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"
    
    @api.model
    def _default_bank_journal_id(self):
        default_company_id = self.default_get(['company_id'])['company_id']
        return self.env['account.journal'].search([('type', 'in', ['cash', 'bank']), ('company_id', '=', default_company_id)], limit=1)
    
    bank_journal_id = fields.Many2one('account.journal', string='Payment Journal', states={'done': [('readonly', True)], 'post': [('readonly', True)]}, check_company=True, domain="[('type', 'in', ['cash', 'bank']), ('company_id', '=', company_id)]",
        default=_default_bank_journal_id, help="The payment method used when the expense is paid by the company.")


class HrExpense(models.Model):
    _inherit = "hr.expense"
    
    @api.model
    def _default_analytic_account_id(self):
        return self.env['account.analytic.account'].search([('operating_unit_ids', '=', self.env.user.default_operating_unit_id.id)], limit=1)
   
    analytic_account_id = fields.Many2one('account.analytic.account',default=_default_analytic_account_id, string='Analytic Account', check_company=True)
    payment_mode = fields.Selection([
        # ("own_account", "Employee (to reimburse)"),
        ("company_account", "Company"),
    ], default='company_account', tracking=True, readonly=True,states={'done': [('readonly', True)], 'approved': [('readonly', True)], 'reported': [('readonly', True)]}, string="Paid By")
    product_id = fields.Many2one('product.product', string='Expense', readonly=True, tracking=True, states={'draft': [('readonly', False)], 'reported': [('readonly', False)], 'refused': [('readonly', False)]}, domain="[('can_be_expensed', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]", ondelete='restrict')