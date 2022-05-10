from odoo import api, fields, models,exceptions,_

class POSPayment(models.Model):
    _inherit = "pos.payment"
    
    operating_unit_id = fields.Many2one(comodel_name="operating.unit",domain="[('user_ids', '=', uid)]",store=True)
    
    @api.model
    def create(self, vals):
        res = super(POSPayment,self).create(vals)
        res.operating_unit_id = self.env.user.default_operating_unit_id.id
        return res