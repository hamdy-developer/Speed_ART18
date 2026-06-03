from odoo import fields, models, api
from odoo.tools import SQL

class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    last_purchase_supplier_id = fields.Many2one('res.partner', string='Last Supplier', readonly=True)

    def _select(self) -> SQL:
        return SQL("%s, last_supplier.partner_id AS last_purchase_supplier_id", super()._select())

    def _from(self) -> SQL:
        return SQL(
            """
            %s
            LEFT JOIN LATERAL (
                SELECT pol.partner_id
                FROM purchase_order_line pol
                JOIN purchase_order po ON po.id = pol.order_id
                WHERE pol.product_id = product.id
                  AND po.state IN ('purchase', 'done')
                  AND pol.company_id = line.company_id
                ORDER BY po.date_order DESC, pol.id DESC
                LIMIT 1
            ) last_supplier ON TRUE
            """,
            super()._from()
        )
