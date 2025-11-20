from odoo.http import request, route

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSale(WebsiteSale):
    @route()
    def shop(
        self,
        page=0,
        category=None,
        search="",
        min_price=0.0,
        max_price=0.0,
        ppg=False,
        **post,
    ):
        request.update_context(whole_pack_price=True)
        return super().shop(
            page=page,
            category=category,
            search=search,
            min_price=min_price,
            max_price=max_price,
            ppg=ppg,
            **post,
        )

    def _get_cart_notification_information(self, order, line_ids):
        """Override to show correct total price for pack products in cart modal"""
        result = super()._get_cart_notification_information(order, line_ids)

        if not result or 'lines' not in result:
            return result

        # Update pack line prices to include components
        for line_info in result['lines']:
            line = order.order_line.filtered(lambda l: l.id == line_info['id'])
            if line and line.product_id.pack_ok:
                # Get all lines related to this pack (parent + children)
                pack_lines = line | line.pack_child_line_ids
                # Calculate total price for the pack including components
                show_tax = order.website_id.show_line_subtotals_tax_selection == 'tax_included'
                total_price = sum(pack_lines.mapped(
                    'price_total' if show_tax else 'price_subtotal'))
                # Update the line price in notification
                line_info['line_price_total'] = total_price

        return result
