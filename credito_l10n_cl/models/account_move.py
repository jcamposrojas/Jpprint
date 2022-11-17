# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo import http
from odoo.http import request
from odoo.exceptions import UserError, Warning
from odoo.tools.float_utils import float_is_zero

import werkzeug.urls

import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    monto_no_pagado = fields.Monetary(string='Monto no pagado', store=True, readonly=True,
            compute="_compute_monto_no_pagado", currency_field='company_currency_id')

    @api.depends('line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
                 'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched')
    def _compute_monto_no_pagado(self):
        for rec in self:
            _logger.info(' 77777 ')
            if rec.state == 'posted':
                reconciled_payments = rec._get_reconciled_payments()
                #reconciled_payments = line._get_reconciled_invoices()
                for a in reconciled_payments:
                    _logger.info(a)
            rec.monto_no_pagado = 0


    @api.model
    def create(self,vals):
        default_move_type = vals.get('move_type') or self._context.get('default_move_type')

        # No aplica para pagos
        if default_move_type in ['out_invoice', 'out_refund']:
            partner = False
            if 'partner_id' in vals:
                partner = self.env['res.partner'].browse(vals['partner_id'])
    
            if self._validate_credit(partner) == False:
                return False

        return super(AccountMove, self).create(vals)


    def _validate_credit(self,partner):
        if partner.credit_on_hold is True:
            raise UserError(_('El Cliente ha sido bloqueado por exceder su Límite de Crédito. Por favor contacte al Administrador.\nGracias!'))
            return False

        if partner.is_credit_limit == True:

            if partner.blocking_limit != 0.0:
                # Facturado NO pagado
                if partner.blocking_limit < partner.invoice_amount:
                    raise UserError(_('The Customer is in blocking stage and has to pay ' + str(partner.invoice_amount)))

            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

            exceeded_amount = partner.credito_usado - partner.credit_limit

            if exceeded_amount > 0:
                raise UserError(_('Lo sentimos, se ha excedido el Límite de Crédito del cliente\n \
                       Límite de Crédito     : %s\n \
                       Credito por NV        : %s\n \
                       Total deuda facturada : %s\n \
                       Cantidad Excedida     : %s')%(partner.credit_limit,partner.credit_amount,partner.invoice_amount,exceeded_amount))
                return False
            return True
