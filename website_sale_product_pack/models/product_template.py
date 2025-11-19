# Copyright 2019 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_combination_info(
        self,
        combination=False,
        product_id=False,
        add_qty=1,
        parent_combination=False,
        only_template=False,
    ):
        """Override to ensure pack prices include component prices in website."""
        # Set context to compute whole pack price for detailed packs
        if self.pack_ok and self.pack_type == "detailed" and self.pack_component_price == "detailed":
            return super(ProductTemplate, self.with_context(whole_pack_price=True))._get_combination_info(
                combination=combination,
                product_id=product_id,
                add_qty=add_qty,
                parent_combination=parent_combination,
                only_template=only_template,
            )
        return super()._get_combination_info(
            combination=combination,
            product_id=product_id,
            add_qty=add_qty,
            parent_combination=parent_combination,
            only_template=only_template,
        )

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
