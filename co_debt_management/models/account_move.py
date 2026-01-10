from odoo import api, fields, models
from odoo.tools import float_is_zero, float_round
class AccountMove(models.Model):
    _inherit = "account.move"
    co_paid_amount = fields.Monetary(
        string="Số tiền đã thanh toán",
        compute="_compute_co_paid_amount"
    )
    co_payment_state = fields.Selection(
        selection=[
            ('not_paid', 'Not Paid'),
            ('partial', 'Partially Paid'),
            ('paid', 'Paid'),
        ],
        string="Co Payment State",
        compute="_compute_co_payment_state",
        store=True,
        tracking=True,
    )

    @api.depends('amount_residual', 'amount_total')
    def _compute_co_payment_state(self):
        for move in self:
            if move.move_type not in ('out_invoice', 'in_invoice'):
                move.co_payment_state = False
                continue

            currency = move.currency_id or self.env.company.currency_id
            total = float_round(move.amount_total, precision_rounding=currency.rounding)
            residual = float_round(move.amount_residual, precision_rounding=currency.rounding)

            if float_is_zero(residual, precision_rounding=currency.rounding):
                move.co_payment_state = 'paid'
            elif float_is_zero(total - residual, precision_rounding=currency.rounding):
                move.co_payment_state = 'not_paid'
            elif 0 < residual < total:
                move.co_payment_state = 'partial'
            else:
                move.co_payment_state = False
    @api.depends('amount_total_signed','amount_residual_signed')
    def _compute_co_paid_amount(self):
        for move in self:
            move.co_paid_amount = move.amount_total_signed - move.amount_residual_signed
