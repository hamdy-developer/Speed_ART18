from odoo import models, fields, api, _


class BaseDocumentLayout(models.TransientModel):
    _inherit = 'base.document.layout'

    header = fields.Binary(related="company_id.header")
    footer = fields.Binary(related="company_id.footer")