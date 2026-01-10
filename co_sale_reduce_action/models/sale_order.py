from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    custom_note = fields.Char(
        string="Custom Note",
        help="Custom field added by custom module."
    )
    co_season = fields.Selection(
        selection=[
            ('vu1', 'Vụ 1'),
            ('vu2', 'Vụ 2'),
            ('vu3', 'Vụ 3')
        ],
        string="Vụ mùa",
        default='vu1',
        store = True
    )

    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        invoice_vals.update({
            'co_season': self.co_season,  # copy từ SO sang Invoice
        })
        return invoice_vals

    @api.onchange('co_season')
    def _onchange_co_season(self):
        if self.co_season:
            for order in self:
                for inv in order.order_line.mapped('invoice_lines.move_id'):
                    inv.co_season = order.co_season



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
            invoice.action_post()
            return {
                'name': "Customer Invoice",
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'view_mode': 'form',
                'res_id': invoice.id,
                'target': 'current',
            }


    # def action_cancel(self):
    #     # Gọi xử lý chuẩn trước
    #     res = super(SaleOrder, self).action_cancel()
    #     out_picking_type = self.env.ref("stock.picking_type_out")
    #
    #     for order in self:
    #         order.state = "cancel"
    #         # chỉ lấy delivery picking
    #         pickings = self.env["stock.picking"].search([
    #             ("origin", "=", order.name),
    #             ("picking_type_id", "=", out_picking_type.id),
    #         ])
    #         for picking in pickings:
    #             picking.unlink()
    #             # if picking.state != "done":
    #             #     picking.unlink()
    #             # else:
    #             #     # kiểm tra nếu đã có phiếu trả hàng (IN) thì bỏ qua
    #             #     existing_returns = self.env["stock.picking"].search([
    #             #         ("origin", "=", picking.name),
    #             #         ("picking_type_id.code", "=", "incoming"),
    #             #     ])
    #             #     if existing_returns:
    #             #         continue  # đã có IN rồi thì không tạo nữa
    #             #
    #             #     picking_type = picking.picking_type_id.return_picking_type_id or picking.picking_type_id
    #             #     new_picking_vals = {
    #             #         "origin": picking.name,
    #             #         "partner_id": picking.partner_id.id,
    #             #         "picking_type_id": picking_type.id,
    #             #         "location_id": picking.location_dest_id.id,
    #             #         "location_dest_id": picking.location_id.id,
    #             #         "move_ids_without_package": [],
    #             #     }
    #             #     new_picking = self.env["stock.picking"].create(new_picking_vals)
    #             #
    #             #     for move in picking.move_ids_without_package:
    #             #         self.env["stock.move"].create({
    #             #             "name": move.name,
    #             #             "product_id": move.product_id.id,
    #             #             "product_uom_qty": move.product_uom_qty,
    #             #             "product_uom": move.product_uom.id,
    #             #             "picking_id": new_picking.id,
    #             #             "location_id": picking.location_dest_id.id,
    #             #             "location_dest_id": picking.location_id.id,
    #             #         })
    #             #
    #             #     if new_picking.state == "draft":
    #             #         new_picking.action_confirm()
    #             #         new_picking.action_assign()
    #             #     if new_picking.state in ("assigned", "confirmed"):
    #             #         new_picking.button_validate()
    #
    #         # Hủy + xóa invoice liên quan
    #         invoices = self.env["account.move"].search([("invoice_origin", "=", order.name)])
    #         for inv in invoices:
    #             # if inv.state != "cancel":
    #             #     inv.button_cancel()
    #             inv.unlink()
    #     return res
    # def action_cancel_without_picking(self):
    #     for order in self:
    #         # Xóa tất cả picking liên quan, bỏ qua return
    #         for picking in order.picking_ids:
    #             picking.move_ids.unlink()
    #             picking.unlink()
    #
    #         # Hủy sale order
    #         order.state = 'cancel'
    #         order.order_line.unlink()
    #     invoices = self.env["account.move"].search([("invoice_origin", "=", order.name)])
    #     for inv in invoices:
    #         # if inv.state != "cancel":
    #         #     inv.button_cancel()
    #         inv.unlink()
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
            for inv in invoices:
                # Tìm tất cả payment liên quan đến invoice
                payments = self.env["account.payment"].search([('reconciled_invoice_ids', 'in', inv.id)])
                for payment in payments:
                    if payment.state != 'draft':
                        payment.action_draft()  # đặt payment về draft
                    payment.unlink()  # hủy payment

                # Đặt invoice về draft nếu chưa ở draft
                if inv.state != 'draft':
                    inv.button_draft()

                # Hủy invoice
                inv.unlink()

            # Hủy sale.order
            order.state = "cancel"

