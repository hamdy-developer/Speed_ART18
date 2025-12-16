# -*- coding: utf-8 -*-
from datetime import date
from odoo.exceptions import UserError
from odoo import models, fields, api, _


class InventoryLocationWizard(models.TransientModel):
    _name = 'inventory.location.wizard'
    _description = 'general ledger vendor wizard'

    name = fields.Char(string="", required=False, )
    date_from = fields.Datetime(string="Date From", required=True, )
    date_to = fields.Datetime(string="Date To", required=True, )
    location_ids = fields.Many2many(comodel_name="stock.location", string="Locations")
    product_ids = fields.Many2many(comodel_name="product.product", string="Products")

    def export_product(self):
        for rec in self:
            if not rec.location_ids:
                rec.location_ids = self.env['stock.location'].sudo().search([]).ids
            if not rec.product_ids:
                rec.product_ids = self.env['product.product'].sudo().search([]).ids
            # if rec.date_from < date(2022, 1, 1):
            #     raise UserError(_("The date must be (1 / 1 / 2022)"))
            if rec.date_to < rec.date_from:
                raise UserError(_("The end date must be after the start date"))
            return self.env.ref('report_stock_move.report_action_id_inventory_location').report_action(self)


class ItemCardWithCost(models.TransientModel):
    _name = 'item_card.with_cost'
    _description = 'Item Card With Cost'

    name = fields.Char(string="", required=False, )
    date_from = fields.Datetime(string="Date From", required=True, )
    date_to = fields.Datetime(string="Date To", required=True, )
    location_ids = fields.Many2many(comodel_name="stock.location", string="Locations",
                                    domain=[('usage', '=', 'internal')])
    product_ids = fields.Many2many(comodel_name="product.product", string="Products",)

    # --- NEW FIELD ---
    lot_ids = fields.Many2many(
        comodel_name='stock.lot',
        string='Lots/Serial Numbers',
        # This domain ensures only lots for the selected products are shown
        domain="[('product_id', 'in', product_ids)]"
    )

    def export_product_with_cost(self):
        for rec in self:
            # If no locations are selected, search for all internal locations
            if not rec.location_ids:
                rec.location_ids = self.env['stock.location'].search([('usage', '=', 'internal')]).ids

            # If lots are selected, products must also be selected
            if rec.lot_ids and not rec.product_ids:
                raise UserError(_("You must select products to filter by lots."))

            # If no products are selected (and no lots), search for all trackable products
            if not rec.product_ids:
                rec.product_ids = self.env['product.product'].search([('tracking', '!=', 'none')]).ids

            if rec.date_to < rec.date_from:
                raise UserError(_("The end date must be after the start date"))

            return self.env.ref('report_stock_move.id_report_item_card_with_cost').report_action(self)
