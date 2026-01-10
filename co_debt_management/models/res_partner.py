from odoo import models, fields, api
from odoo.osv import expression
import logging
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    co_invoice_count = fields.Integer(
        string="Hóa đơn chưa thanh toán",
        compute = "_compute_co_invoice_count"
    )
    def _compute_co_invoice_count(self):
        for partner in self:
            partner.co_invoice_count = self.env['account.move'].search_count([
                ('payment_state', 'not in', ['paid', 'in_payment']),
                ('partner_id', '=', partner.id),
                ('move_type', '=', 'out_invoice'),
                ('payment_state', '!=', 'paid')

            ])
    def action_open_customer_invoices(self):
        self.ensure_one()
        return {
            'name' : 'Hóa đơn công nợ của khách hàng',
            'type' : 'ir.actions.act_window',
            'res_model' : 'account.move',
            'view_mode' : 'tree,form',
            'domain' : [
                ('payment_state', 'not in', ['paid', 'in_payment']),
                ('partner_id', '=', self.id),
                ('move_type', '=', 'out_invoice'),
                ('payment_state', '!=', 'paid')
            ],
            'context': {
            'default_partner_id': self.id,
            'group_by': 'co_season',   # nhóm theo co_season
            'expand': True             # mặc định expand các nhóm
        },
        }

    def action_view_sale_order(self):
        action = self.env['ir.actions.act_window']._for_xml_id('sale.act_res_partner_2_sale_order')
        all_child = self.with_context(active_test=False).search([('id', 'child_of', self.ids)])
        action['domain'] = [
            ('partner_id', 'in', all_child.ids),
            ('state', '!=', 'cancel')  # Loại bỏ các đơn hàng đã hủy
        ]
        return action

    def _compute_sale_order_count(self):
        # retrieve all children partners and prefetch 'parent_id' on them
        all_partners = self.with_context(active_test=False).search_fetch(
            [('id', 'child_of', self.ids)],
            ['parent_id'],
        )
        sale_order_groups = self.env['sale.order']._read_group(
            domain=expression.AND([
                self._get_sale_order_domain_count(),
                [('partner_id', 'in', all_partners.ids)],
                [('state', '!=', 'cancel')]  # Loại bỏ đơn hàng đã hủy
            ]),
            groupby=['partner_id'],
            aggregates=['__count']
        )
        self_ids = set(self._ids)

        self.sale_order_count = 0
        for partner, count in sale_order_groups:
            while partner:
                if partner.id in self_ids:
                    partner.sale_order_count += count
                    _logger.info(
                        f"Partner {partner.name} (ID: {partner.id}): sale_order_count = {partner.sale_order_count}")
                partner = partner.parent_id