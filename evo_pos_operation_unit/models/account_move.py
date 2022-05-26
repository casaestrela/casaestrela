from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    # operating_unit_id = fields.Many2one('operating.unit','Operating Unit')
    origin = fields.Char("Source Origin")
    pos_session_id = fields.Many2one("pos.session", string="POS Session",
                                     readonly=1)

    @api.model_create_multi
    def create(self, values):

        for record in values:
            context = self._context.copy()
            if context.get("pos_session_id", None):
                record.update(
                    {
                        "pos_session_id": context.get("pos_session_id"),
                        "origin": "Point Of Sale",
                    }
                )

        res = super(AccountMove, self).create(values)
        if res.pos_session_id:
            if res.pos_session_id.config_id:
                res.operating_unit_id = (
                    res.pos_session_id.config_id.operating_unit_id.id
                )
        return res


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model_create_multi
    def create(self, values):
        res = super(AccountMoveLine, self).create(values)
        for data in res:
            if data.operating_unit_id:
                analytic_account_id = (
                    self.env["account.analytic.account"]
                    .sudo()
                    .search(
                        [("operating_unit_ids", "=", data.operating_unit_id.id)],
                        limit=1,
                    )
                )
                if analytic_account_id:
                    data.analytic_account_id = analytic_account_id.id
        return res
