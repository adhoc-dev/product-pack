# Copyright 2019 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _price_compute(self, price_type, uom=None, currency=None, company=None, date=False):
        prices = super(ProductProduct, self)._price_compute(price_type, uom, currency, company, date)

        return prices

        for product_id in prices:
            product = self.browse(product_id)
            if product.pack_ok and product.pack_type == 'detailed' and product.pack_component_price == 'detailed':
                pack_price = 0.00
                for component in product.pack_line_ids:
                    pack_price += component.product_id._price_compute(price_type=price_type, uom=component.product_id.uom_id, currency=currency, company=company, date=date).get(component.product_id.id, 0) * component.quantity

                prices[product.id] = pack_price

        return prices

    @api.constrains("pack_line_ids")
    def check_website_published(self):
        for rec in self.filtered("is_published"):
            unpublished = rec.pack_line_ids.mapped("product_id").filtered(
                lambda x: not x.is_published
            )
            if unpublished:
                raise ValidationError(
                    _(
                        "You can't add unpublished products "
                        "(%(unpublished_products)s)"
                        "to a published pack (%(pack_name)s)"
                    )
                    % {
                        "unpublished_products": ", ".join(unpublished.mapped("name")),
                        "pack_name": rec.name,
                    }
                )
