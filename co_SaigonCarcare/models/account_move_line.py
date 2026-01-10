from odoo import models, fields, api

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    price_subtotal_untaxed = fields.Monetary(
        string="Chưa giảm giá",
        currency_field='currency_id',
        store=True,
        compute='_compute_price_subtotal_untaxed'
    )
    co_unit = fields.Selection(
        selection=[
            ('xe', 'xe'),
            ('cap', 'cặp'),
            ('cai', 'cái'),
            ('bo', 'bộ'),            
        ],
        string="Đơn vị tính",
        default='xe',
        store = True
    )

    @api.depends('quantity', 'price_unit')
    def _compute_price_subtotal_untaxed(self):
        for line in self:
            line.price_subtotal_untaxed = line.quantity * line.price_unit
