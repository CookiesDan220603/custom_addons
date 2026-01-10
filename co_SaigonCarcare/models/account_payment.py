from odoo import models, fields, api

class AccountPayment(models.Model):
    _inherit = 'account.payment'
    _mail_post_access = 'read'
    
    def _message_auto_subscribe_notify(self, partner_ids, template):
        # Tắt auto subscribe
        return
    
    def message_post(self, **kwargs):
        # Chặn gửi message
        return False

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
        # Lấy email mặc định nếu user không có email
        ctx = dict(self.env.context)
        if not self.env.user.email:
            ctx['mail_create_nosubscribe'] = True
            ctx['mail_notrack'] = True
            # Hoặc set email mặc định
            self = self.with_context(**ctx)
        return super(AccountPayment, self).action_post()