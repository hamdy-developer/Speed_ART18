# -*- coding: utf-8 -*-

from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    x_brand = fields.Char('Brand')
