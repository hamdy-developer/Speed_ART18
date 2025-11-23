# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT


class WizardStockCard(models.TransientModel):
    _name = 'wizard.stock.card'
    _description = 'stock card wizard'

    product_id = fields.Many2one(comodel_name='product.product', string='Product', required=True)
    location_id = fields.Many2one(comodel_name='stock.location', string='Location', required=True)
    owner_id = fields.Many2one(comodel_name='res.partner', string='Owner')
    date_from = fields.Date(string='From', required=True)
    date_to = fields.Date(string='To',required=True)

    def print_pdf_stock_card(self, context=None):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_from': self.date_from,
                'date_to': self.date_to,
                'location_id': self.location_id.id,
                'owner_id': self.owner_id.id,
                'product_id': self.product_id.id,
            },
        }
        return self.env.ref('dvit_stock_card_report.action_stock_card').report_action(self, data=data)


class ReportStockCard(models.AbstractModel):
    _name = 'report.dvit_stock_card_report.stock_card_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        location_id = data['form']['location_id']
        product_id = data['form']['product_id']
        owner_id = data['form']['owner_id']

        init_moves = self.env['stock.move'].sudo().search([
            ('restrict_partner_id', '=', owner_id),
            ('product_id', '=', product_id),
            ('date', '<', date_from),
            ('state', '=', 'done'),
            '|',('location_id', '=', location_id),
                ('location_dest_id','=',location_id),
                ],order="date")
        init_in = sum([m.product_uom_qty for m in init_moves if m.location_dest_id.id == location_id and 
                        m.product_uom == m.product_id.uom_id]) or 0
        init_out = sum([m.product_uom_qty for m in init_moves if m.location_id.id == location_id and 
                        m.product_uom == m.product_id.uom_id]) or 0
        for m in init_moves.filtered(lambda m: m.product_uom != m.product_id.uom_id and m.location_dest_id == location_id):
            xqty = m.product_uom_qty
            init_in +=  xqty * l.product_id.uom_id.factor if l.product_id.uom_id.factor != 1 else l.product_uom.factor * xqty
        for m in init_moves.filtered(lambda m: m.product_uom != m.product_id.uom_id and m.location_id == location_id):
            xqty = m.product_uom_qty
            init_out +=  xqty * l.product_id.uom_id.factor if l.product_id.uom_id.factor != 1 else l.product_uom.factor * xqty
            
        # init_cost = sum([m.price_unit * m.product_uom_qty for m in init_moves if m.location_dest_id.id == location_id]) - \
        #     sum([m.price_unit * m.product_uom_qty for m in init_moves if m.location_id.id == location_id])
        init_data = {
            'in': init_in,
            'out': init_out,
        }
        # print '>>>>>>>> init_data', init_data
        moves = self.env['stock.move'].sudo().search([
            ('restrict_partner_id', '=', owner_id),
            ('product_id', '=', product_id),
            ('date', '>=', date_from),
            ('date', '<=', date_to),
            ('state', '=', 'done'),
            '|',('location_id', '=', location_id),
                ('location_dest_id','=',location_id),
                ],order="date")

        if not moves:
            raise UserError('No stock moves for this product in selected location !!')

        data['location'] = self.env['stock.location'].browse(location_id)
        data['product'] = self.env['product.product'].browse(product_id)
        data['owner'] = self.env['res.partner'].browse(owner_id)
        data['init_bal'] = init_data

        docargs = {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_from': date_from,
            'date_to': date_to,
            'docs': moves,
            'data': data,
        }

        # print '>>>>>>>>>>> data:', data
        return docargs
