from odoo import api, fields, models,exceptions,_

class ReasonMaster(models.Model):
    _name = "reason.master"
    _description = "Reason Master"
    
    name = fields.Char('Name')
    