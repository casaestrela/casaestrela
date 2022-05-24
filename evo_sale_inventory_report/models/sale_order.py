from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    product_default_code = fields.Char(related="product_id.default_code")
    pending_delivery_qty = fields.Float(
        compute="_get_to_delivery_qty",
        string="Pending Delivery Quantity",
        readonly=True,
        digits="Product Unit of Measure",
    )
    invoice_names = fields.Char(compute="_get_invoice_name", string="Invoices")
    delivery_order_names = fields.Char(
        compute="_get_delivery_order_name", string="Delivery Order"
    )

    @api.depends("move_ids")
    def _get_delivery_order_name(self):
        for line in self:
            line.delivery_order_names = ""
            name_list = []
            for move_id in line.move_ids:
                name_list.append(move_id.picking_id.name)
            if name_list:
                line.delivery_order_names = ", ".join(name_list)

    @api.depends("invoice_lines")
    def _get_invoice_name(self):
        for line in self:
            line.invoice_names = ""
            name_list = []
            for invoice in line.invoice_lines:
                name_list.append(invoice.move_id.name)
            if name_list:
                line.invoice_names = ", ".join(name_list)

    @api.depends(
        "qty_delivered", "product_uom_qty",
    )
    def _get_to_delivery_qty(self):
        for line in self:
            line.pending_delivery_qty = line.product_uom_qty - line.qty_delivered
