from odoo import models, fields, api, _
import logging
from odoo.tools.misc import formatLang


_logger = logging.getLogger(__name__)
class SaleOrder(models.Model):
    _inherit = 'sale.order'
    consultant_id = fields.Many2one(
        'res.users',
        string='Người tư vấn',
        required=True,
        default=lambda self: self.env.user,
        tracking=True,
    )
    license_plate = fields.Char(
        string="Biển số xe",
        tracking=True,
    )
    car_brand = fields.Char(
        string="Hiệu xe",
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
        tracking=True,
        states={'draft': [('readonly', False)]}
    )

    partner_street = fields.Char(
        string="Địa chỉ",
        tracking=True,
        states={'draft': [('readonly', False)]}
    )
    discount_total = fields.Float(
        string="Chiết khấu toàn đơn hàng (%)",
        default='',
        help="Áp dụng mức giảm giá phần trăm cho toàn bộ đơn hàng."
    )

    amount_total_without_discount = fields.Monetary(
        string="Tổng chưa giảm giá",
        currency_field='currency_id',
        store=True,
        compute='_compute_amount_total_without_discount'
    )
    

    tax_totals_amount = fields.Monetary(string='Tổng thanh toán', currency_field='currency_id',
                                        compute='_compute_tax_totals_amount', store=False)

    @api.depends('product_uom_qty')
    def _compute_price_subtotal_untaxed(self):
        for order in self:
            order.tax_totals_amount = order.amount_total
    @api.depends('amount_total')
    def _compute_tax_totals_amount(self):
        for order in self:
            # Lấy số tiền tổng thuế hoặc tổng thanh toán từ amount_total (hoặc tax_totals nếu bạn muốn)
            # Ví dụ lấy amount_total, bạn có thể sửa tùy theo logic thực tế
            order.tax_totals_amount = order.amount_total

    @api.depends('order_line.price_unit', 'order_line.product_uom_qty')
    def _compute_amount_total_without_discount(self):
        for order in self:
            total = 0.0
            for line in order.order_line.filtered(lambda l: not l.display_type):
                total += line.price_unit * line.product_uom_qty
            order.amount_total_without_discount = total

    @api.onchange('discount_total')
    def _onchange_discount_total(self):
        for order in self:
            for line in order.order_line:
                # Tính số tiền giảm giá cho mỗi dòng
                price = line.price_unit * line.product_uom_qty
                line.discount_line = price * (order.discount_total or 0.0) / 100.0

    @api.depends('order_line.tax_id', 'order_line.price_unit', 'amount_total', 'amount_untaxed', 'currency_id',
                 'discount_total')


    def action_create_invoices(self):
        for order in self:
            for picking in order.picking_ids:
                if picking.state == "draft":
                    picking.action_confirm()
                    picking.action_assign()
                if picking.state in ("assigned", "confirmed"):
                    for move in picking.move_ids:
                        move.quantity = move.product_uom_qty
                    picking.button_validate()

            invoice = order._create_invoices()
            invoice.write({
                'license_plate': order.license_plate,
                'car_brand': order.car_brand,
                'discount_total': order.discount_total,
                'delivery_date': order.delivery_date,
                'receiving_date': order.receiving_date,
            })
            for line in invoice.invoice_line_ids:
                    line.discount = invoice.discount_total
            return {
                'name': "Customer Invoice",
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'view_mode': 'form',
                'res_id': invoice.id,
                'target': 'current',
            }
    def action_cancel_without_picking(self):
        out_picking_type = self.env.ref("stock.picking_type_out")
        for order in self:

            # chỉ lấy delivery picking
            pickings = self.env["stock.picking"].search([
                ("origin", "=", order.name),
                ("picking_type_id", "=", out_picking_type.id),
            ])
            for picking in pickings:
                if picking.state != "done":
                    picking.unlink()
                else:
                    # kiểm tra nếu đã có phiếu trả hàng (IN) thì bỏ qua
                    existing_returns = self.env["stock.picking"].search([
                        ("origin", "=", picking.name),
                        ("picking_type_id.code", "=", "incoming"),
                    ])
                    if existing_returns:
                        continue  # đã có IN rồi thì không tạo nữa

                    picking_type = picking.picking_type_id.return_picking_type_id or picking.picking_type_id
                    new_picking_vals = {
                        "origin": picking.name,
                        "partner_id": picking.partner_id.id,
                        "picking_type_id": picking_type.id,
                        "location_id": picking.location_dest_id.id,
                        "location_dest_id": picking.location_id.id,
                        "move_ids_without_package": [],
                    }
                    new_picking = self.env["stock.picking"].create(new_picking_vals)

                    for move in picking.move_ids_without_package:
                        self.env["stock.move"].create({
                            "name": move.name,
                            "product_id": move.product_id.id,
                            "product_uom_qty": move.product_uom_qty,
                            "product_uom": move.product_uom.id,
                            "picking_id": new_picking.id,
                            "location_id": picking.location_dest_id.id,
                            "location_dest_id": picking.location_id.id,
                        })

                    if new_picking.state == "draft":
                        new_picking.action_confirm()
                        new_picking.action_assign()
                    if new_picking.state in ("assigned", "confirmed"):
                        new_picking.button_validate()

            # Hủy + xóa invoice liên quan
            # Hủy + xóa invoice và payment liên quan
            invoices = self.env["account.move"].search([("invoice_origin", "=", order.name)])
        
            _logger.info(f"=== Canceling order {order.name} ===")
            _logger.info(f"Found invoices to delete: {invoices.mapped('name')}")
            
            for inv in invoices:
                # CHỈ tìm payment mà invoice này là DUY NHẤT invoice được reconcile
                all_payments = self.env["account.payment"].search([
                    ('reconciled_invoice_ids', 'in', inv.id)
                ])
                
                # Lọc chỉ lấy payment CHỈ reconcile với invoice này
                payments_to_delete = self.env["account.payment"]
                for payment in all_payments:
                    # Kiểm tra payment này chỉ reconcile với invoice hiện tại
                    if len(payment.reconciled_invoice_ids) == 1 and payment.reconciled_invoice_ids.id == inv.id:
                        payments_to_delete |= payment
                        _logger.info(f"Will delete payment {payment.name} - only reconciled to {inv.name}")
                    else:
                        _logger.warning(f"SKIP payment {payment.name} - reconciled to multiple invoices: {payment.reconciled_invoice_ids.mapped('name')}")
                
                # Xóa các payment an toàn
                for payment in payments_to_delete:
                    try:
                        _logger.info(f"Deleting payment {payment.name}")
                        if payment.state == 'posted':
                            payment.action_draft()
                        payment.unlink()
                    except Exception as e:
                        _logger.error(f"Cannot delete payment {payment.name}: {str(e)}")

                # Bỏ reconcile trước khi xóa invoice
                try:
                    inv.line_ids.remove_move_reconcile()
                except Exception as e:
                    _logger.warning(f"Cannot remove reconcile for {inv.name}: {str(e)}")
                
                # Đặt invoice về draft nếu chưa ở draft
                if inv.state != 'draft':
                    inv.button_draft()

                # Xóa invoice
                _logger.info(f"Deleting invoice {inv.name}")
                inv.unlink()


            # Hủy sale.order
            order.state = "cancel"

    def action_print_quotes(self):
        self.ensure_one()
        # Gọi report action để in PDF
        return self.env.ref('co_SaigonCarcare.quotes_report_action').report_action(self)
    def action_print_construction_order(self):
        self.ensure_one()
        # Gọi report action để in PDF
        return self.env.ref('co_SaigonCarcare.construction_report_action').report_action(self)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        for rec in self:
            if rec.partner_id:
                rec.partner_phone = rec.partner_id.phone
                rec.partner_street = rec.partner_id.street

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            if rec.partner_id:
                if 'partner_phone' in vals:
                    rec.partner_id.phone = vals['partner_phone']
                if 'partner_street' in vals:
                    rec.partner_id.street = vals['partner_street']
        return res

    def create(self, vals):
        rec = super().create(vals)
        if rec.partner_id:
            if vals.get('partner_phone'):
                rec.partner_id.phone = vals['partner_phone']
            if vals.get('partner_street'):
                rec.partner_id.street = vals['partner_street']
        return rec