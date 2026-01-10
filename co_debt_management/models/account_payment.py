from odoo import api, fields, models

class AccountPayment(models.Model):
    _inherit = "account.payment"

    deferred_original_move_ids = fields.Many2many(
        'account.move',
        string="Hóa đơn gốc",
        compute="_compute_deferred_original_move_ids",
        store=False
    )
    @api.depends('move_id.line_ids.matched_debit_ids.debit_move_id.move_id',
                 'move_id.line_ids.matched_credit_ids.credit_move_id.move_id')
    def _compute_deferred_original_move_ids(self):
        for payment in self:
            invoices = self.env['account.move']
            for line in payment.move_id.line_ids:
                reconciles = (
                    line.matched_debit_ids.debit_move_id.move_id |
                    line.matched_credit_ids.credit_move_id.move_id
                )
                invoices |= reconciles.filtered(lambda m: m.move_type in ['out_invoice', 'in_invoice'])
            payment.deferred_original_move_ids = invoices
