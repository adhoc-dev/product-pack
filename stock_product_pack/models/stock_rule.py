# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    @api.model
    def run(self, procurements):
        """ If 'run' is called on a pack product storable.
         we remove the procurement with this product pack.
        """
        for procurement in procurements:
            if (
                procurement.product_id
                and procurement.product_id.pack_ok
                and procurement.product_id.dont_create_move
                and procurement.product_id.pack_type == "detailed"
            ):
                procurements.remove(procurement)
                sale_order_id = procurement.values.get("sale_line_id")
                if sale_order_id:
                    self.env["sale.order.line"].browse(
                        sale_order_id
                    ).qty_delivered = procurement.product_qty

        return super(ProcurementGroup, self).run(procurements)
