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