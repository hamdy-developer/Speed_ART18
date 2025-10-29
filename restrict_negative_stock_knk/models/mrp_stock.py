# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare


class Picking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        for picking in self:
            for move in picking.move_ids_without_package:
                product = move.product_id
                done_qty = move.quantity
                available_qty = product.qty_available
                rounding = product.uom_id.rounding

                if float_compare(done_qty, available_qty, precision_rounding=rounding) == 1:
                    raise UserError(_("There is no stock available for some products."))

        return super().button_validate()


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def button_mark_done(self):
        for production in self:
            if production.components_availability == _("Not Available"):
                raise UserError(_("There is no stock available for some products."))
        return super(MrpProduction, self).button_mark_done()
