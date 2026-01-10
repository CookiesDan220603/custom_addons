from odoo import models, fields, api

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        # Nếu có invoice active, lấy journal tiền mặt và amount residual
        active_id = self._context.get('active_id')
        if active_id:
            invoice = self.env['account.move'].browse(active_id)
            if invoice and invoice.move_type in ('out_invoice','in_invoice'):
                cash_journal = self.env['account.journal'].search([('type','=','cash')], limit=1)
                if cash_journal:
                    res['journal_id'] = cash_journal.id
                res['amount'] = invoice.amount_residual
        return res
    #
    # def action_create_payments(self):
    #     payments = super().action_create_payments()
    #     # Tự confirm tất cả payment vừa tạo
    #     for payment in payments:
    #         payment.action_post()
    #     return payments
