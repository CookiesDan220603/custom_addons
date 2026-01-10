from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    # ========= FIELDS =========
    qty_available = fields.Float(string='Qty Available',
                                 readonly=True)
    out_of_stock = fields.Boolean(string='Out of Stock',
                                  compute='_compute_out_of_stock',
                                  store=True)
    discount_line = fields.Monetary(
        string="Giảm giá (VND)",
        help="Số tiền giảm giá trực tiếp cho dòng này."
    )
    price_subtotal_untaxed = fields.Monetary(
        string="Thành tiền",
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

    @api.depends('product_uom_qty', 'price_unit')
    def _compute_price_subtotal_untaxed(self):
        for line in self:
            line.price_subtotal_untaxed = line.product_uom_qty*line.price_unit
    @api.depends('product_uom_qty', 'price_unit', 'discount_line', 'tax_id')
    def _compute_amount(self):
        for line in self:
            price_before_discount = line.price_unit * line.product_uom_qty
            price_after_discount = price_before_discount - line.discount_line

            taxes = line.tax_id.compute_all(
                price_after_discount,
                currency=line.order_id.currency_id,
                quantity=1.0,
                product=line.product_id,
                partner=line.order_id.partner_shipping_id
            )

            line.update({
                'price_subtotal': taxes['total_excluded'],
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
            })

    def _convert_to_tax_base_line_dict(self, **kwargs):
        self.ensure_one()
        # Tính lại price_unit đã trừ tiền giảm discount_line
        if self.product_uom_qty:
            price_unit_after_discount = (self.price_unit * self.product_uom_qty - self.discount_line) / self.product_uom_qty
        else:
            price_unit_after_discount = self.price_unit

        return self.env['account.tax']._convert_to_tax_base_line_dict(
            self,
            partner=self.order_id.partner_id,
            currency=self.order_id.currency_id,
            product=self.product_id,
            taxes=self.tax_id,
            price_unit=price_unit_after_discount,
            quantity=self.product_uom_qty,
            discount=0.0,  # tránh tính double discount
            price_subtotal=self.price_subtotal,
            **kwargs,
        )
    @api.depends('product_template_id')
    def _compute_qty_available(self):
        for line in self:
            # Truy xuất qty_available từ product_template_id nếu có
            line.qty_available = line.product_template_id.qty_available
    # Compute
    @api.depends('product_uom_qty', 'product_template_id', 'order_id.order_line.product_uom_qty')
    def _compute_out_of_stock(self):
        for line in self:
            if not line.product_template_id:
                line.out_of_stock = False
                continue

            same_product_lines = line.order_id.order_line.filtered(
                lambda l: l.product_template_id == line.product_template_id
            )

            total_qty = sum(same_product_lines.mapped('product_uom_qty'))

            if total_qty >= line.qty_available:
                for l in same_product_lines:
                    l.out_of_stock = True
            else:
                for l in same_product_lines:
                    l.out_of_stock = False

    # ========= ONCHANGE =========
    def _prepare_invoice_line(self, **optional_values):
        res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        res['co_unit'] = self.co_unit
        return res



