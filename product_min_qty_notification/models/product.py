import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    min_qty = fields.Float(string='Minimum Quantity')

class ProductProduct(models.Model):
    _inherit = 'product.product'

    min_qty = fields.Float(string='Minimum Quantity', related='product_tmpl_id.min_qty', readonly=False)

    def _cron_check_min_qty(self):
        _logger.info("Cron job 'Check Product Minimum Quantity' started.")
        products = self.search([('is_storable', '=', True)])
        products_below_min = products.filtered(lambda p: p.qty_available < p.min_qty)
        _logger.info(f"Found {len(products_below_min)} products below minimum quantity.")

        if products_below_min:
            group = self.env.ref('product_min_qty_notification.group_min_qty_notification')
            recipient_partners = group.user_ids.mapped('partner_id')
            recipient_emails = [partner.email for partner in recipient_partners if partner.email]

            if not recipient_emails:
                _logger.warning("No recipients found for minimum quantity notification.")
                return

            subject = _("Product Quantity Alert")
            body = _("Dear User,<br/><br/>The following products are below their minimum quantity:<br/><ul>")
            for product in products_below_min:
                body += _(f"<li><a href=\"/web#id={product.id}&model=product.product\">{product.name}</a>: Current Quantity: {product.qty_available}, Minimum Quantity: {product.min_qty}</li>")
            body += _("</ul><br/>Please take the necessary actions.<br/><br/>Thanks,<br/>Odoo")

            mail_values = {
                'subject': subject,
                'body_html': body,
                'email_to': ', '.join(recipient_emails),
                'auto_delete': False,
            }
            self.env['mail.mail'].sudo().create(mail_values).send()
            _logger.info("Minimum quantity notification email sent successfully.")
        _logger.info("Cron job 'Check Product Minimum Quantity' finished.")