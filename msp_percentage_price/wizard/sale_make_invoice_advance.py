from odoo import models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _prepare_invoice_values(self, order, name, amount, so_line):
        invoice_vals = super(SaleAdvancePaymentInv, self)._prepare_invoice_values(
            order=order, name=name, amount=amount, so_line=so_line
        )
        if invoice_vals:
            if invoice_vals.get("invoice_line_ids", False):
                invoice_vals["invoice_line_ids"][0][2].update(
                    {
                        "msp_percentage": so_line.msp_percentage,
                        "msp_subtotal": so_line.msp_subtotal,
                    }
                )
        return invoice_vals
