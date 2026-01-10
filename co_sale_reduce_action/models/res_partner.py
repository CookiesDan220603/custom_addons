from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = 'res.partner'

    email = fields.Boolean(default=False, required=False)