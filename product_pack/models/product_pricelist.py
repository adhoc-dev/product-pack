from odoo import models


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    def _get_product_price(self, product, quantity, uom=None, date=False, **kwargs):
        """Compute the pricelist price for the specified product, qty & uom.

        Note: self.ensure_one()

        :returns: unit price of the product, considering pricelist rules
        :rtype: float
        """
        self.ensure_one()
        if product._is_pack_to_be_handled():
            pack_lines = product.sudo().pack_line_ids.mapped("product_id")
            pack_line_prices = self._compute_price_rule(
                pack_lines, quantity, uom=uom, date=date, **kwargs
            )
            pack_price = self._compute_price_rule(
                product, quantity, uom=uom, date=date, **kwargs
            )[product.id][0]
            for line in product.sudo().pack_line_ids:
                pack_price += line._compute_price(
                    base_price=pack_line_prices[line.product_id.id][0]
                )
            return pack_price
        else:
            return super()._get_product_price(
                product=product, quantity=quantity, uom=uom, date=date, **kwargs
            )

    def _get_products_price(self, products, quantity, uom=None, date=False, **kwargs):
        """Compute the pricelist prices for the specified products, qty & uom.

        Note: self.ensure_one()

        :returns: dict{product_id: product price}, considering the current pricelist
        :rtype: dict
        """
        packs, no_packs = products.split_pack_products()
        res = super()._get_products_price(
            no_packs, quantity=quantity, uom=uom, date=date, **kwargs
        )
        for pack in packs:
            res[pack.id] = self._get_product_price(
                product=pack, quantity=quantity, uom=uom, date=date, **kwargs
            )
        return res
