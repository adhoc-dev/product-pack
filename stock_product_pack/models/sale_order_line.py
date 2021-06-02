# Copyright 2019 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _compute_qty_delivered(self):
        super()._compute_qty_delivered()
        parent_pack_lines = self.filtered("pack_parent_line_id").mapped(
            "pack_parent_line_id"
        )
        for pack_line in parent_pack_lines:
            components = pack_line.pack_child_line_ids.mapped("product_id")
            prodct_moves = pack_line.order_id.order_line.move_ids.filtered(
                lambda m: m.product_id.id in components.ids
            )
            if components and prodct_moves:
                if all([m.state == "done" for m in prodct_moves]):
                    pack_line.qty_delivered = pack_line.product_uom_qty
                else:
                    pack_line.qty_delivered = 0.0
