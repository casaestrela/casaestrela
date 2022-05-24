from odoo import api, fields, models


class OperatingUnit(models.Model):
    _inherit = "operating.unit"
    
    vendor_next_seq_number = fields.Integer('Vendor Next Sequence Number',default=1)
    next_seq_number = fields.Integer('Invoice Next Sequence Number',default=1)