# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProductProduct(models.Model):
    _inherit = 'product.product'


    mod_id = fields.Char('Moadian ID', copy=False, index='btree_not_null')