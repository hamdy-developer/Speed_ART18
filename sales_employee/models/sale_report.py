# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = 'sale.report'

    sales_employee_id = fields.Many2one('hr.employee', string='Sales Employee', readonly=True)
    amount_paid = fields.Float(string='Amount Paid', readonly=True)

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res["sales_employee_id"] = "s.sales_employee_id"
        res["amount_paid"] = """COALESCE((
            SELECT SUM(
                CASE WHEN COALESCE(m.amount_total, 0) = 0 THEN 0.0
                ELSE (inv_l.price_total / m.amount_total) * (m.amount_total_signed - m.amount_residual_signed)
                END
            )
            FROM account_move_line inv_l
            JOIN account_move m ON m.id = inv_l.move_id
            JOIN sale_order_line_invoice_rel rel ON rel.invoice_line_id = inv_l.id
            JOIN sale_order_line sol ON sol.id = rel.order_line_id
            WHERE sol.order_id = l.order_id
              AND sol.product_id = l.product_id
              AND m.state = 'posted'
              AND m.move_type IN ('out_invoice', 'out_refund')
        ), 0.0)"""
        return res

    def _group_by_sale(self):
        group_by = super()._group_by_sale()
        group_by = f"""
            {group_by},
            s.sales_employee_id"""
        return group_by
