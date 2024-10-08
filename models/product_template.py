# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'


    mod_id = fields.Char('Moadian ID', compute='_compute_modid', inverse='_set_modid', search='_search_modid')

    @api.depends('product_variant_ids.mod_id')
    def _compute_modid(self):
        self.mod_id = False
        for template in self:
            # TODO master: update product_variant_count depends and use it instead
            variant_count = len(template.product_variant_ids)
            if variant_count == 1:
                template.mod_id = template.product_variant_ids.mod_id
            elif variant_count == 0:
                archived_variants = template.with_context(active_test=False).product_variant_ids
                if len(archived_variants) == 1:
                    template.mod_id = archived_variants.mod_id

    def _search_modid(self, operator, value):
        query = self.with_context(active_test=False)._search([('product_variant_ids.mod_id', operator, value)])
        return [('id', 'in', query)]

    def _set_modid(self):
        variant_count = len(self.product_variant_ids)
        if variant_count == 1:
            self.product_variant_ids.mod_id = self.mod_id
        elif variant_count == 0:
            archived_variants = self.with_context(active_test=False).product_variant_ids
            if len(archived_variants) == 1:
                archived_variants.mod_id = self.mod_id
