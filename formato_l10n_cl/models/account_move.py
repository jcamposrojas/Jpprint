from num2words import num2words
from odoo import api, fields, models, _

import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def _l10n_cl_edi_amount_to_text(self):
        self.ensure_one()
        amount_i = int(round(self.amount_total, 0))
        return num2words(amount_i, lang='es').upper()

    @api.model
    def _get_sale_orders(self):
        return ', '.join(self.mapped("invoice_line_ids.sale_line_ids.order_id.name"))

    @api.model
    def _get_sellers(self):
        return ', '.join(self.mapped("invoice_line_ids.sale_line_ids.order_id.user_id.name"))

    @api.model
    def _get_ref_clients(self):
        refs = self.mapped("invoice_line_ids.sale_line_ids.order_id.client_order_ref")
        st = str(refs).strip("[]")
        if st != 'False':
            return ', '.join(refs)
        return ''



class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def _get_warehouse(self):
        return ', '.join(self.mapped("sale_line_ids.order_id.warehouse_id.code"))
