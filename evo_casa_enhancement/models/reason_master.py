from odoo import _, api, exceptions, fields, models


class ReasonMaster(models.Model):
    _name = "reason.master"
    _description = "Reason Master"

    name = fields.Char("Name")
