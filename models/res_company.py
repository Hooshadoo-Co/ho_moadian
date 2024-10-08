# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _

class ResCompanyInherit(models.Model):
    _inherit = 'res.company'


    org_api_url = fields.Char(string="API URL")
    fiscal_id = fields.Char(string="Fiscal ID")
    pkey_file = fields.Binary(string='Private Key File', help='Upload the Private Key')