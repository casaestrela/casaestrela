from odoo import models


class PosSession(models.Model):
    _inherit = "pos.session"

    def _validate_session(self):
        context = self._context.copy()
        context.update({"pos_session_id": self.id})
        res = super(PosSession, self.with_context(context))._validate_session()
        return res
