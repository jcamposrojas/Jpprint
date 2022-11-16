# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class AccountInvoiceReference(models.Model):
    _inherit = 'l10n_cl.account.invoice.reference'

    stock_picking_id = fields.Many2one('stock.picking', ondelete='cascade', string='Documento Original')



