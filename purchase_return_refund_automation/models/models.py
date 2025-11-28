from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockPickingInherit(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        res = super(StockPickingInherit, self).button_validate()
        for picking in self:
            # Check if it's an outgoing shipment and it's a return of a receipt
            if picking.picking_type_code == 'outgoing' and picking.origin and 'Return of' in picking.origin:
                original_picking_name = picking.origin.replace('Return of ', '')
                original_picking = self.env['stock.picking'].search([
                    ('name', '=', original_picking_name),
                    ('picking_type_code', '=', 'incoming')
                ], limit=1)

                if original_picking and original_picking.purchase_id:
                    self._create_refund_from_return(picking, original_picking)
        return res

    def _create_refund_from_return(self, return_picking, original_picking):
        purchase_order = original_picking.purchase_id

        original_bill = purchase_order.invoice_ids.filtered(
            lambda inv: inv.state == 'posted' and inv.move_type == 'in_invoice'
        )
        original_bill = original_bill[0] if original_bill else None

        journal = self.env['account.journal'].search([
            ('type', '=', 'purchase'),
            ('company_id', '=', purchase_order.company_id.id)
        ], limit=1)
        if not journal:
            raise UserError(_('Please define a purchase journal for the company %s.') % purchase_order.company_id.name)

        invoice_line_ids = []
        for move in return_picking.move_ids.filtered(lambda m: m.state == 'done' and m.quantity > 0):
            po_line = purchase_order.order_line.filtered(
                lambda l: l.product_id == move.product_id
            )
            if not po_line:
                continue

            po_line = po_line[0]

            invoice_line_ids.append((0, 0, {
                'product_id': move.product_id.id,
                'name': move.product_id.name,
                'quantity': move.quantity,
                'product_uom_id': move.product_uom.id,
                'price_unit': po_line.price_unit,
                'tax_ids': [(6, 0, po_line.taxes_id.ids)],
                'purchase_line_id': po_line.id,
            }))

        if not invoice_line_ids:
            return

        refund_invoice = self.env['account.move'].with_context(default_move_type='in_refund').create({
            'move_type': 'in_refund',
            'partner_id': return_picking.partner_id.id,
            'invoice_date': fields.Date.today(),
            'journal_id': journal.id,
            'invoice_origin': return_picking.name,
            'reversed_entry_id': original_bill.id if original_bill else False,
            'invoice_line_ids': invoice_line_ids,
        })

        refund_invoice.action_post()

        return_picking.message_post(body=_('Vendor Refund %s created.') % refund_invoice.name)
        if purchase_order:
            purchase_order.message_post(body=_('Vendor Refund %s created for return %s.') % (refund_invoice.name, return_picking.name))

        return refund_invoice
