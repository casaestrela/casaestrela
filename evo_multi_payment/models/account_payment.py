from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    invoice_id = fields.Many2one("account.move", string="Invoice")

    def reconcile(self):
        """ Reconcile the current move lines all together.
        :return: A dictionary representing a summary of what has been done during the reconciliation:
                * partials:             A recorset of all account.partial.reconcile created during the reconciliation.
                * full_reconcile:       An account.full.reconcile record created when there is nothing left to reconcile
                                        in the involved lines.
                * tax_cash_basis_moves: An account.move recordset representing the tax cash basis journal entries.
        """
        results = {}

        if not self:
            return results

        # List unpaid invoices
        not_paid_invoices = self.move_id.filtered(
            lambda move: move.is_invoice(include_receipts=True)
            and move.payment_state not in ("paid", "in_payment")
        )

        # ==== Check the lines can be reconciled together ====
        company = None
        account = None
        for line in self:
            if line.reconciled:
                raise UserError(
                    _(
                        "You are trying to reconcile some entries that are already reconciled."
                    )
                )
            if (
                not line.account_id.reconcile
                and line.account_id.internal_type != "liquidity"
            ):
                raise UserError(
                    _(
                        "Account %s does not allow reconciliation. First change the configuration of this account to allow it."
                    )
                    % line.account_id.display_name
                )
            if line.move_id.state != "posted":
                raise UserError(_("You can only reconcile posted entries."))
            if company is None:
                company = line.company_id
            elif line.company_id != company:
                raise UserError(
                    _("Entries doesn't belong to the same company: %s != %s")
                    % (company.display_name, line.company_id.display_name)
                )
            if account is None:
                account = line.account_id
            elif line.account_id != account:
                raise UserError(
                    _("Entries are not from the same account: %s != %s")
                    % (account.display_name, line.account_id.display_name)
                )

        sorted_lines = self.sorted(
            key=lambda line: (line.date_maturity or line.date, line.currency_id)
        )

        # ==== Collect all involved lines through the existing reconciliation ====

        involved_lines = sorted_lines
        involved_partials = self.env["account.partial.reconcile"]
        current_lines = involved_lines
        current_partials = involved_partials
        while current_lines:
            current_partials = (
                current_lines.matched_debit_ids + current_lines.matched_credit_ids
            ) - current_partials
            involved_partials += current_partials
            current_lines = (
                current_partials.debit_move_id + current_partials.credit_move_id
            ) - current_lines
            involved_lines += current_lines

        # ==== Create partials ====

        partial_amount = self.env.context.get("amount", False)
        if partial_amount:
            reconcile = sorted_lines._prepare_reconciliation_partials()
            if reconcile:
                reconcile[0].update(
                    {
                        "amount": partial_amount,
                        "debit_amount_currency": partial_amount,
                        "credit_amount_currency": partial_amount,
                    }
                )
        else:
            reconcile = sorted_lines._prepare_reconciliation_partials()

        partials = self.env["account.partial.reconcile"].create(reconcile)
        # Track newly created partials.
        results["partials"] = partials
        involved_partials += partials

        # ==== Create entries for cash basis taxes ====

        is_cash_basis_needed = account.user_type_id.type in ("receivable", "payable")
        if is_cash_basis_needed and not self._context.get("move_reverse_cancel"):
            tax_cash_basis_moves = partials._create_tax_cash_basis_moves()
            results["tax_cash_basis_moves"] = tax_cash_basis_moves

        # ==== Check if a full reconcile is needed ====

        if involved_lines[0].currency_id and all(
            line.currency_id == involved_lines[0].currency_id for line in involved_lines
        ):
            is_full_needed = all(
                line.currency_id.is_zero(line.amount_residual_currency)
                for line in involved_lines
            )
        else:
            is_full_needed = all(
                line.company_currency_id.is_zero(line.amount_residual)
                for line in involved_lines
            )
        if is_full_needed:

            # ==== Create the exchange difference move ====

            if self._context.get("no_exchange_difference"):
                exchange_move = None
            else:
                exchange_move = involved_lines._create_exchange_difference_move()
                if exchange_move:
                    exchange_move_lines = exchange_move.line_ids.filtered(
                        lambda line: line.account_id == account
                    )

                    # Track newly created lines.
                    involved_lines += exchange_move_lines

                    # Track newly created partials.
                    exchange_diff_partials = (
                        exchange_move_lines.matched_debit_ids
                        + exchange_move_lines.matched_credit_ids
                    )
                    involved_partials += exchange_diff_partials
                    results["partials"] += exchange_diff_partials

                    exchange_move._post(soft=False)

            # ==== Create the full reconcile ====

            results["full_reconcile"] = self.env["account.full.reconcile"].create(
                {
                    "exchange_move_id": exchange_move and exchange_move.id,
                    "partial_reconcile_ids": [(6, 0, involved_partials.ids)],
                    "reconciled_line_ids": [(6, 0, involved_lines.ids)],
                }
            )

        # Trigger action for paid invoices
        not_paid_invoices.filtered(
            lambda move: move.payment_state in ("paid", "in_payment")
        ).action_invoice_paid()

        return results


class Payment(models.Model):
    _inherit = "account.payment"

    ad_line_ids = fields.One2many("advance.payment.line", "payment_id")
    ad_line_total = fields.Monetary(
        string="Line Total", compute="_compute_ad_line_total"
    )

    @api.depends("ad_line_ids.reconcile_amount")
    def _compute_ad_line_total(self):
        for rec in self:
            line_total = 0.0
            if rec.ad_line_ids:
                for line in rec.ad_line_ids:
                    line_total += line.reconcile_amount
            rec.ad_line_total = line_total
            rec.amount = line_total
            # rec.amount = rec.ad_line_total

    @api.model
    def create(self, values):
        res = super(Payment, self).create(values)
        for rec in self:
            ad_lines_total = 0.0
            if rec.ad_line_ids:
                for line in rec.ad_line_ids:
                    ad_lines_total += line.reconcile_amount
                if ad_lines_total > round(rec.amount, 2) or ad_lines_total < round(
                    rec.amount, 2
                ):
                    raise ValidationError(
                        "Allocation amount cannot be more or less then Payment amount."
                    )

        return res

    def write(self, values):
        res = super(Payment, self).write(values)
        for rec in self:
            ad_lines_total = 0.0
            if rec.ad_line_ids:
                for line in rec.ad_line_ids:
                    ad_lines_total += line.reconcile_amount
                if round(ad_lines_total, 2) > round(rec.amount, 2) or round(
                    ad_lines_total, 2
                ) < round(rec.amount, 2):
                    raise ValidationError(
                        "Allocation amount cannot be more or less then Amount."
                    )
        return res

    @api.onchange("payment_type", "partner_type", "partner_id", "currency_id")
    def _onchange_to_get_vendor_invoices(self):
        if (
            self.payment_type in ["inbound", "outbound"]
            and self.partner_type
            and self.partner_id
            and self.currency_id
        ):
            self.ad_line_ids = [(6, 0, [])]
            if self.payment_type == "inbound" and self.partner_type == "customer":
                invoice_type = "out_invoice"
            elif self.payment_type == "outbound" and self.partner_type == "customer":
                invoice_type = "out_refund"
            elif self.payment_type == "outbound" and self.partner_type == "supplier":
                invoice_type = "in_invoice"
            else:
                invoice_type = "in_refund"
            invoice_recs = self.env["account.move"].search(
                [
                    ("partner_id", "child_of", self.partner_id.id),
                    ("state", "=", "posted"),
                    ("move_type", "=", invoice_type),
                    ("payment_state", "!=", "paid"),
                ]
            )
            payment_invoice_values = []
            for invoice_rec in invoice_recs:
                payment_invoice_values.append([0, 0, {"invoice_id": invoice_rec}])
            self.ad_line_ids = payment_invoice_values
        else:
            self.ad_line_ids = [(5, 0, 0)]

    def action_post(self):
        super(Payment, self).action_post()
        for payment in self:
            if payment.ad_line_ids:
                if payment.amount < sum(payment.ad_line_ids.mapped("reconcile_amount")):
                    raise UserError(
                        _(
                            "The sum of the reconcile amount of listed invoices are greater than payment's amount."
                        )
                    )

            for line_id in payment.ad_line_ids:
                if not line_id.reconcile_amount:
                    continue
                if line_id.amount_total <= line_id.reconcile_amount:
                    self.ensure_one()
                    if payment.payment_type == "inbound":
                        lines = payment.move_id.line_ids.filtered(
                            lambda line: line.credit > 0
                        )
                        lines += line_id.invoice_id.line_ids.filtered(
                            lambda line: line.account_id == lines[0].account_id
                            and not line.reconciled
                        )
                        lines.reconcile()
                    elif payment.payment_type == "outbound":
                        lines = payment.move_id.line_ids.filtered(
                            lambda line: line.debit > 0
                        )
                        lines += line_id.invoice_id.line_ids.filtered(
                            lambda line: line.account_id == lines[0].account_id
                            and not line.reconciled
                        )
                        lines.reconcile()
                else:
                    self.ensure_one()
                    if payment.payment_type == "inbound":
                        lines = payment.move_id.line_ids.filtered(
                            lambda line: line.credit > 0
                        )
                        lines += line_id.invoice_id.line_ids.filtered(
                            lambda line: line.account_id == lines[0].account_id
                            and not line.reconciled
                        )
                        lines.with_context(amount=line_id.reconcile_amount).reconcile()
                    elif payment.payment_type == "outbound":
                        lines = payment.move_id.line_ids.filtered(
                            lambda line: line.debit > 0
                        )
                        lines += line_id.invoice_id.line_ids.filtered(
                            lambda line: line.account_id == lines[0].account_id
                            and not line.reconciled
                        )
                        lines.with_context(amount=line_id.reconcile_amount).reconcile()
        return True
