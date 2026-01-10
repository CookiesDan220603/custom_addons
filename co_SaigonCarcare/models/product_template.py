
from odoo import models, fields, api, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        if 'purchase_ok' in fields_list:
            defaults['purchase_ok'] = False
        if 'sale_ok' in fields_list:
            defaults['sale_ok'] = False
        if 'detailed_type' in fields_list:
            defaults['detailed_type'] = 'product'
        return defaults

