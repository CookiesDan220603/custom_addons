from odoo import models, fields,api
from odoo.tools import float_is_zero, float_round

class AccountMove(models.Model):
    _inherit = "account.move"
    payment_reference = fields.Char(readonly=True)
    license_plate = fields.Char(
        string="Biển số xe",
        readonly=True,
        tracking=True,
        
    )

    car_brand = fields.Char(
        string="Hiệu xe",
        readonly=True,
        tracking=True,
        
    )
    receiving_date = fields.Date(
        string="Ngày nhận xe",
        default=fields.Date.context_today,
        tracking=True,
        
    )
    delivery_date = fields.Date(
        string="Ngày giao xe",
        tracking=True,
        
    )
    partner_phone = fields.Char(
        string="Số điện thoại",
        related='partner_id.phone',
        tracking=True,
        states = {'draft': [('readonly', False)]}
    )

    partner_street = fields.Char(
        string="Địa chỉ",
        related='partner_id.street',
        tracking=True,
        states={'draft': [('readonly', False)]}
    )
    discount_total = fields.Float(
        string="Chiết khấu tổng (%)",
        default=0.0,
        states={'draft': [('readonly', False)]},
        tracking=True,
    )
    amount_total_without_discount = fields.Monetary(
        string="Tổng chưa giảm giá",
        currency_field='currency_id',
        store=True,
        compute='_compute_amount_total_without_discount'
    )

    @api.depends('line_ids.price_unit', 'line_ids.quantity', 'line_ids.discount')
    def _compute_amount_total_without_discount(self):
        for move in self:
            total = 0.0
            for line in move.line_ids:
                # Chỉ tính dòng có giá trị quantity (ví dụ dòng sản phẩm)
                # Có thể bỏ điều kiện hoặc thay đổi tùy logic
                if line.quantity:
                    # Tính tổng chưa trừ discount (nếu bạn muốn)
                    total += line.price_unit * line.quantity
            move.amount_total_without_discount = total
    @api.onchange('discount_total')
    def _onchange_discount_total(self):
        for record in self:
            for line in record.line_ids:
                # Cập nhật discount của từng dòng theo discount_total của hóa đơn
                line.discount = record.discount_total or 0.0

    @api.model
    def create(self, vals):
        move = super().create(vals)

        if move.discount_total:
            for line in move.invoice_line_ids:
                line.discount = move.discount_total

        return move
    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        if 'invoice_date_due' in fields_list:
            defaults['invoice_date_due'] = False
        return defaults
    def action_print_invoice(self):
        """Action để in hóa đơn - mở preview trong chrome"""
        self.ensure_one()

        # Gọi report action để in PDF
        return self.env.ref('co_SaigonCarcare.invoice_report_action').report_action(self)


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


