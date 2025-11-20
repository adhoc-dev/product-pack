# Copyright 2019 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _get_combination_info_variant(self, **kwargs):
        """Override to ensure pack prices include component prices in website."""
        # Set context to compute whole pack price for detailed packs
        if self.pack_ok and self.pack_type == "detailed" and self.pack_component_price == "detailed":
            return super(ProductProduct, self.with_context(whole_pack_price=True))._get_combination_info_variant(**kwargs)
        return super()._get_combination_info_variant(**kwargs)

    def _get_configurator_display_price(
        self, product_or_template, quantity, date, currency, pricelist, **kwargs
    ):
        """Override to ensure pack prices include component prices in configurator."""
        # Check if this is a pack product with detailed pricing
        is_pack = (
            hasattr(product_or_template, 'pack_ok')
            and product_or_template.pack_ok
            and product_or_template.pack_type == "detailed"
            and product_or_template.pack_component_price == "detailed"
        )

        if is_pack:
            # Add whole_pack_price context for pack products
            product_or_template = product_or_template.with_context(
                whole_pack_price=True)

        return super()._get_configurator_display_price(
            product_or_template, quantity, date, currency, pricelist, **kwargs
        )

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
