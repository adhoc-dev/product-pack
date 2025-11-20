from odoo.http import request

from odoo.addons.sale.controllers.product_configurator import (
    SaleProductConfiguratorController,
)


class SaleProductConfiguratorController(SaleProductConfiguratorController):
    def _get_basic_product_information(self, product_or_template, pricelist, combination, **kwargs):
        """Override to ensure pack prices include component prices in configurator modal"""
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

        return super()._get_basic_product_information(
            product_or_template, pricelist, combination, **kwargs
        )
