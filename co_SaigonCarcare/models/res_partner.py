from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = 'res.partner'
    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        if 'email' in fields_list:
            defaults['email'] = False
        return defaults