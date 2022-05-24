from odoo import api, fields, models,exceptions,_

class AccountPayment(models.Model):
    _inherit = "account.payment"
    
    cheque_number = fields.Char('Cheque Number')
    cheque_date = fields.Date('Cheque Date')
    operating_unit_id = fields.Many2one(
        comodel_name="operating.unit",
        domain="[('user_ids', '=', uid)]",
        # compute="_compute_operating_unit_id",
        store=True,
    )
    
    @api.model
    def create(self, vals):
        res = super(AccountPayment,self).create(vals)
        res.operating_unit_id = self.env.user.default_operating_unit_id.id
        return res
    
    