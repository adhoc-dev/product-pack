# Copyright 2021 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=W8110
from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _compute_qty_delivered(self):
        """Compute pack delivered pack quantites according to its components
        deliveries"""
        super()._compute_qty_delivered()
        main_pack_lines = self.filtered("pack_parent_line_id").mapped(
            "pack_parent_line_id"
        )
        for line in main_pack_lines.filtered(
            lambda x: x.qty_delivered_method == "stock_move"
            and x.pack_child_line_ids
            and x.product_uom_qty
        ):
            delivered_packs = []
            # We filter non qty lines of editable packs
            for pack_line in line.pack_child_line_ids.filtered("product_uom_qty"):
                # If a component isn't delivered, the pack isn't as well
                if not pack_line.qty_delivered:
                    delivered_packs.append(0)
                    break
                qty_per_pack = pack_line.product_uom_qty / line.product_uom_qty
                delivered_packs.append(pack_line.qty_delivered / qty_per_pack)
            line.qty_delivered = delivered_packs and min(delivered_packs) or 0.0

    def _prepare_invoice_line(self, **optional_values):
        """Override to handle pack lines in returns.

        When a return is being processed, pack parent lines don't have stock moves,
        so their qty_delivered doesn't update automatically. We need to calculate
        the correct quantity based on the components being returned.
        """
        res = super()._prepare_invoice_line(**optional_values)
        if self.pack_child_line_ids and self.product_id.pack_ok:
            components_being_returned = self.pack_child_line_ids.filtered(
                lambda x: x.qty_to_invoice < 0
            )
            if components_being_returned and res.get("quantity", 0) == 0:
                refund_quantities = []
                for comp in components_being_returned:
                    qty_per_pack = (
                        comp.product_uom_qty / self.product_uom_qty
                        if self.product_uom_qty
                        else 0
                    )
                    if qty_per_pack:
                        packs_to_refund = comp.qty_to_invoice / qty_per_pack
                        refund_quantities.append(packs_to_refund)
                if refund_quantities:
                    pack_qty_to_refund = max(refund_quantities)
                    res["quantity"] = pack_qty_to_refund
        return res
