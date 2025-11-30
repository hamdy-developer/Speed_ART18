# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class StockQuantityHistory(models.TransientModel):
    _inherit = 'stock.quantity.history'

    def open_at_date(self):
        action = super(StockQuantityHistory, self).open_at_date()
        tree_view_id = self.env.ref('dvit_inventory_at_date.inventory_at_date_view_tree').id
        if self.env.context.get('inventory_at_date'):
            action['views'] = [(tree_view_id, 'tree')]
        return action


class ProductTemplate(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def _get_inventory_at_date_action(self, domain=None, extend=False):
        """ Returns an action to open (non-inventory adjustment) quant view.
        Depending of the context (user have right to be inventory mode or not),
        the list view will be editable or readonly.

        :param domain: List for the domain, empty by default.
        :param extend: If True, enables form, graph and pivot views. False by default.
        """
        self = self._set_view_context()
        if not self.env['ir.config_parameter'].sudo().get_param('stock.skip_quant_tasks'):
            self._quant_tasks()
        ctx = dict(self.env.context or {})
        ctx['inventory_report_mode'] = True
        ctx['inventory_at_date'] = True
        ctx.pop('group_by', None)
        action = {
            'name': _('Inventory At Date'),
            'view_type': 'tree',
            'view_mode': 'list,form',
            'res_model': 'stock.quant',
            'type': 'ir.actions.act_window',
            'context': ctx,
            'domain': domain or [],
        }

        target_action = self.env.ref('stock.dashboard_open_quants', False)
        if target_action:
            action['id'] = target_action.id

        form_view = self.env.ref('stock.view_stock_quant_form_editable').id
        if self.env.context.get('inventory_mode') and self.env.user.has_group('stock.group_stock_manager'):
            action['view_id'] = self.env.ref('stock.view_stock_quant_tree_editable').id
        else:
            action['view_id'] = self.env.ref('dvit_inventory_at_date.product_inventory_at_date_view_tree').id
        action.update({
            'views': [
                (action['view_id'], 'list'),
                (form_view, 'form'),
            ],
        })
        if extend:
            action.update({
                'view_mode': 'tree,form,pivot,graph',
                'views': [
                    (action['view_id'], 'list'),
                    (form_view, 'form'),
                    (self.env.ref('stock.view_stock_quant_pivot').id, 'pivot'),
                    (self.env.ref('stock.stock_quant_view_graph').id, 'graph'),
                ],
            })
        return action
