from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # ========= FIELDS =========
    qty_available = fields.Float(string='Qty Available',
                                 related='product_id.qty_available',
                                 readonly=True)
    out_of_stock = fields.Boolean(string='Out of Stock',
                                  compute='_compute_out_of_stock',
                                  store=True)
    
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

    



