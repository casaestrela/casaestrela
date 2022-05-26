from odoo import fields, models


class ReasonMaster(models.Model):
    _name = "reason.master"
    _description = "Reason Master"

    name = fields.Char("Name")
