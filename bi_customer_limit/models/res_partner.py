# -*- coding: utf-8 -*-

from odoo import models, fields, api , _
from collections import defaultdict

import json

import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    # ==== Pagos ====
    res_partner_credits = fields.Text(string="Pagos",groups="account.group_account_invoice,account.group_account_readonly",
        compute='_compute_res_partner_credits')

    def _compute_res_partner_credits(self):
        self.ensure_one()
        #
        invoices = self.env['account.move'].search([('partner_id','=',self.id),('state','=','posted'),('payment_state','in',['not_paid', 'partial'])])
        #invoices = self.env['account.move'].search([('partner_id','=',self.id)])

        self.res_partner_credits = json.dumps(False)
        total = 0.0

        payments_widget_vals = {'title':_('Credito por pagar'), 'content': []}

        for move in invoices:
            if not move.is_invoice(include_receipts=True):
                continue

            if move.state != 'posted' \
                    or move.payment_state not in ('not_paid', 'partial') \
                    or not move.is_invoice(include_receipts=True):
                continue

            # Solo credito
#            if not move.is_inbound():
#                continue

            pay_term_lines = move.line_ids\
                .filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))

            domain = [
                ('balance', '<', 0.0),
                ('account_id', 'in', pay_term_lines.account_id.ids),
                ('move_id.state', '=', 'posted'),
                ('partner_id', '=', move.commercial_partner_id.id),
                ('reconciled', '=', False),
                '|', ('amount_residual', '!=', 0.0), ('amount_residual_currency', '!=', 0.0),
            ]
            #domain.append(('move_id', '=', move.id))

            #_logger.info(domain)
            for line in self.env['account.move.line'].search(domain):
                if line.currency_id == move.currency_id:
                    # Same foreign currency.
                    amount = abs(line.amount_residual_currency)
                else:
                    # Different foreign currencies.
                    amount = move.company_currency_id._convert(
                        abs(line.amount_residual),
                        move.currency_id,
                        move.company_id,
                        line.date,
                    )

                #_logger.info(line.ref or line.move_id.name)
                if move.currency_id.is_zero(amount):
                    continue

                rec = {
                    'journal_name': line.ref or line.move_id.name,
                    'amount': amount,
                    'currency': move.currency_id.symbol,
                    'id': line.id,
                    'move_id': line.move_id.id,
                    'position': move.currency_id.position,
                    'digits': [69, move.currency_id.decimal_places],
                    'payment_date': fields.Date.to_string(line.date),
                }
                payments_widget_vals['content'].append(rec)

                total = total + amount;

            #if not payments_widget_vals['content']:
            #    continue


        if total > 0:
            payments_widget_vals['outstanding'] = True
            payments_widget_vals['total'] = total
        _logger.info(payments_widget_vals)
        self.res_partner_credits = json.dumps(payments_widget_vals)

