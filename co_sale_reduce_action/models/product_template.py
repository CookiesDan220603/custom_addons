from email.policy import default

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    purchase_ok = fields.Boolean(default=False, required=False)
    sale_ok = fields.Boolean(default=False, required=False)
    detailed_type = fields.Selection(default = 'product',required=False)
