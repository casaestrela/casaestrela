from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    default_code = fields.Char(
        "Internal Reference", index=True, store=True, readonly="1"
    )  # compute='compute_internal_reference',

    @api.model
    def default_get(self, field_list):
        res = super(ProductTemplate, self).default_get(field_list)

        res.update(
            {"available_in_pos": True}
        )

        return res

    @api.model_create_multi
    def create(self, vals_list):

        for vals in vals_list:
            code = ""
            if vals.get("categ_id", False):
                category_id = self.env["product.category"].browse(vals["categ_id"])
                number = str(category_id.next_number).rjust(4, "0")
                code = "{} - {}".format(category_id.category_prefix, number)
                vals["default_code"] = code
                category_id.next_number += 1
        return super(ProductTemplate, self).create(vals_list)

    def write(self, vals):
        code = ""
        if "categ_id" in vals:
            category_id = self.env["product.category"].browse(vals["categ_id"])
            number = str(category_id.next_number).rjust(4, "0")
            code = "{} - {}".format(category_id.category_prefix, number)
            vals["default_code"] = code
            category_id.next_number += 1
        return super(ProductTemplate, self).write(vals)


class ProductProduct(models.Model):
    _inherit = "product.product"

    default_code = fields.Char(
        "Internal Reference", index=True
    )  # ,store=True,compute='compute_internal_reference'

    @api.model
    def default_get(self, field_list):
        res = super(ProductProduct, self).default_get(field_list)

        res.update(
            {"available_in_pos": True}
        )

        return res

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            code = ""
            if vals.get("categ_id", False):
                if not vals.get("default_code"):
                    category_id = self.env["product.category"].browse(vals["categ_id"])
                    number = str(category_id.next_number).rjust(4, "0")
                    code = "{} - {}".format(category_id.category_prefix, number)
                    vals["default_code"] = code
        return super(ProductProduct, self).create(vals_list)

    def write(self, vals):
        code = ""
        if "categ_id" in vals:
            category_id = self.env["product.category"].browse(vals["categ_id"])
            number = str(category_id.next_number).rjust(4, "0")
            code = "{} - {}".format(category_id.category_prefix, number)
            vals["default_code"] = code
        return super(ProductProduct, self).write(vals)
