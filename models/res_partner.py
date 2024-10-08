# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _

class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'


    mod_top = fields.Selection([('1', 'Haghighi'),('2', 'Hoghoughi'),('3', 'Mosharekat Madani'),('4', 'Atba'),('5', 'End Consumer')],string='Modaian Buyer Type', default='1')
