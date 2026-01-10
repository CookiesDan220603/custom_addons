from odoo import models, fields

class AccountMove(models.Model):
    _inherit = "account.move"

    co_season = fields.Selection(
        selection=[
            ('vu1', 'Vụ 1'),
            ('vu2', 'Vụ 2'),
            ('vu3', 'Vụ 3')
        ],
        string="Vụ mùa"
    )
    def action_print_invoice(self):
        """Action để in hóa đơn - mở preview trong chrome"""
        self.ensure_one()

        # Gọi report action để in PDF
        return self.env.ref('co_sale_reduce_action.invoice_report_action').report_action(self)
