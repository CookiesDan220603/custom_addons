from odoo import models, fields, api

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)

        if 'journal_id' in fields_list:
            # Tìm journal loại 'cash'
            cash_journal = self.env['account.journal'].search([('type','=','cash')], limit=1)
            if cash_journal:
                defaults['journal_id'] = cash_journal.id

        return defaults
    # Trong model account.payment hoặc sale.order
    def _track_subtype(self, init_values):
        # Tắt tracking để không gửi email
        return False
    def action_post(self):
    # Tắt gửi email
        return super(AccountPayment, self.with_context(mail_create_nosubscribe=True, mail_create_nolog=True, mail_notrack=True)).action_post()