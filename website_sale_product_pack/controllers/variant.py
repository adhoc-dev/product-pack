from odoo.addons.website_sale.controllers.variant import WebsiteSaleVariantController


class WebsiteSaleVariantController(WebsiteSaleVariantController):
    def get_combination_info_website(
        self, product_template_id, product_id, combination, add_qty, **kw
    ):
        if "context" in kw:
            kw["context"].update({"whole_pack_price": True})
        else:
            kw["context"] = {"whole_pack_price": True}
        return super(WebsiteSaleVariantController, self).get_combination_info_website(
            product_template_id, product_id, combination, add_qty, **kw
        )
