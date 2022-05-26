from odoo import api, fields, models


class AdvancePaymentLine(models.Model):
    _name = "advance.payment.line"
    _description = "Advance Payment Line"

    invoice_id = fields.Many2one("account.move", string="Invoice")
    payment_id = fields.Many2one("account.payment", string="Payment")
    currency_id = fields.Many2one(related="invoice_id.currency_id")
    origin = fields.Char(related="invoice_id.invoice_origin")
    date_invoice = fields.Date(related="invoice_id.invoice_date")
    date_due = fields.Date(related="invoice_id.invoice_date_due")
    payment_state = fields.Selection(related="payment_id.state", store=True)
    pay_amount = fields.Monetary(string="Net Amount",
                                 compute="_compute_pay_amount")
    # pay_amount = fields.Monetary(string='Pay Amount')
    reconcile_amount = fields.Monetary(string="Pay Amount")
    # reconcile_amount = fields.Monetary(string='Net Amount',
    # compute='compute_reconcile_amount')
    untax_amount = fields.Monetary(
        related="invoice_id.amount_untaxed", string="Untaxed Amount"
    )
    tax_amount = fields.Monetary(related="invoice_id.amount_tax",
                                 string="Tax Amount")
    amount_total = fields.Monetary(related="invoice_id.amount_total")
    residual = fields.Monetary(related="invoice_id.amount_residual")
    invoice_tds_id = fields.Many2one("account.tax", string="TDS")
    invoice_tds_amount = fields.Monetary(string="TDS Amount")

    @api.onchange("reconcile_amount", "invoice_tds_id")
    def onchange_pay_amount_invoice_tds_id(self):
        for rec in self:
            if rec.reconcile_amount and rec.invoice_tds_id:
                final_amount = (rec.reconcile_amount * rec.invoice_tds_id.amount) / 100
                rec.invoice_tds_amount = final_amount
            else:
                rec.invoice_tds_amount = 0.0

    @api.depends("reconcile_amount", "invoice_tds_amount")
    def _compute_pay_amount(self):
        for rec in self:
            rec.pay_amount = rec.reconcile_amount + rec.invoice_tds_amount

    # @api.onchange('pay_amount', 'invoice_tds_id')
    # def onchange_pay_amount_invoice_tds_id(self):
    #     for rec in self:
    #         if rec.pay_amount and rec.invoice_tds_id:
    #             final_amount = (rec.pay_amount * rec.invoice_tds_id.amount) / 100
    #             rec.invoice_tds_amount = final_amount
    #         else:
    #             rec.invoice_tds_amount = 0.0

    # @api.depends('pay_amount', 'invoice_tds_amount')
    # def compute_reconcile_amount(self):
    #     for rec in self:
    #         rec.reconcile_amount = rec.pay_amount + rec.invoice_tds_amount
