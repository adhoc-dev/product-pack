# Copyright 2019 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.constrains("is_published")
    def check_website_published(self):
        """For keep the consistent and prevent bugs within the e-commerce,
        we force that all childs of a parent pack
        stay publish when the parent is published.
        Also if any of the childs of the parent pack became unpublish,
        we unpublish the parent."""
        for rec in self.filtered(lambda x: x.pack_ok and x.is_published):
            unpublished = rec.pack_line_ids.mapped("product_id").filtered(
                lambda p: not p.is_published
            )
            if unpublished:
                raise ValidationError(
                    _(
                        "You can't unpublished products (%(unpublished_products)s) to a"
                        "published pack (%(pack_name)s)"
                    )
                    % {
                        "unpublished_products": ", ".join(unpublished.mapped("name")),
                        "pack_name": rec.name,
                    }
                )

        for rec in self.filtered(
            lambda x: not x.is_published and x.used_in_pack_line_ids
        ):
            published = rec.used_in_pack_line_ids.mapped("parent_product_id").filtered(
                "is_published"
            )
            if published:
                raise ValidationError(
                    _(
                        "You can't unpublished product (%(product_name)s) for a"
                        "published pack parents (%(pack_parents)s)"
                    )
                    % {
                        "product_name": rec.name,
                        "pack_parents": ", ".join(published.mapped("name")),
                    }
                )

    # Necessary for the website_sale_product_pack module because the price in /shop
    # is calculated by the product.template.price_compute method
    def price_compute(
        self, price_type, uom=False, currency=False, company=False, date=False
    ):
        templates_with_packs, templates_without_packs = self.split_pack_products()
        prices = super(ProductTemplate, templates_without_packs).price_compute(
            price_type, uom, currency, company, date
        )
        for template in templates_with_packs.with_context(prefetch_fields=False):
            pack_line_prices = template.sudo().pack_line_ids._pack_line_price_compute(
                price_type, uom, currency, company, date
            )
            prices[template.id] = sum(pack_line_prices.values())
        return prices
