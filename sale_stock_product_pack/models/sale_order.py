# Copyright 2021 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=W8110
from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_invoiceable_lines(self, final=False):
        """Override to ensure pack parent lines are included when their
        components are being invoiced/refunded.

        When processing returns, only component lines have stock moves, so only
        they would be included in the refund. This method ensures that if pack
        component lines are invoiceable (due to returns), their parent pack line
        is also included if it has a price.
        """
        lines = super()._get_invoiceable_lines(final=final)
        pack_components_in_lines = lines.filtered("pack_parent_line_id")
        if pack_components_in_lines:
            pack_parent_lines = pack_components_in_lines.mapped("pack_parent_line_id")
            has_return = any(
                comp.qty_to_invoice < 0 for comp in pack_components_in_lines
            )
            additional_pack_lines = pack_parent_lines.filtered(
                lambda x: x.id not in lines.ids
                and (x.pack_component_price != "detailed" or x.price_unit > 0)
                and (x.qty_to_invoice != 0 or (x.qty_invoiced > 0 and has_return))
            )
            if additional_pack_lines:
                result_lines = self.env["sale.order.line"]
                for line in lines:
                    result_lines |= line
                    if (
                        line.pack_parent_line_id
                        and line.pack_parent_line_id in additional_pack_lines
                    ):
                        result_lines |= line.pack_parent_line_id
                        additional_pack_lines -= line.pack_parent_line_id
                return result_lines
        return lines
