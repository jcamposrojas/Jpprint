# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo import http
from odoo.http import request
from odoo.exceptions import UserError, Warning
from odoo.tools.float_utils import float_is_zero
from collections import defaultdict

import json

import werkzeug.urls

import logging

_logger = logging.getLogger(__name__)

class res_pertner(models.Model):
    _inherit = "res.partner"
    
    is_credit_limit     = fields.Boolean(string=_("Activar"))
    credit_on_hold      = fields.Boolean(string=_("Bloquear Cliente"))
    company_id          = fields.Many2one('res.company', string="Compañia", default=lambda s: s.env.company, required=True)
    company_currency_id = fields.Many2one(related='company_id.currency_id', string=_('Company Currency'),
                              readonly=True, store=True,
                              help=_('Utility field to express amount currency'))
    credit_limit        = fields.Monetary(string=_("Límite de Crédito"), currency_field='company_currency_id')
    blocking_limit      = fields.Monetary(string=_("Límite de bloqueo para facturas impagas"), currency_field='company_currency_id',
                              help=_("Monto máximo adeudado en facturas no pagadas"))
    credit_amount       = fields.Monetary(string=_('Crédito por NV'), currency_field='company_currency_id',
                              compute="_compute_credit_amount",
                              help=_("Crédito por Notas de Venta no facturadas"))
    used_credit         = fields.Monetary(string=_('Crédito Usado'), currency_field='company_currency_id',
                              compute="_compute_credit_amount",
                              help=_("Crédito usado en Notas de Venta y Facturas"))
    payment_amount      = fields.Monetary(string=_('Monto por Pagos'), currency_field='company_currency_id',
                              compute="_compute_payment_amount",
                              help=_("Abonos de Cliente"))

    invoice_amount      = fields.Monetary(string=_('Monto por Facturas'), currency_field='company_currency_id',
                              compute="_compute_invoice_amount",
                              help=_("Abonos de Cliente"))

    credito_usado       = fields.Monetary(string=_('Crédito usado'), currency_field='company_currency_id',
                              compute="_compute_credito_usado",
                              help=_("Crédito usado = Facturas + Notas de venta - Abonos"))

    # Se deberia modificar para incluir abonos o pagos
    balance_invoice_ids = fields.One2many('account.move', 'partner_id', string=_('Facturas'), compute="_compute_invoice_list")
                              #domain=[('move_type', 'in', ['out_invoice','out_refund']),('payment_state', 'not in', ['paid']),('state','=',('posted'))]) 
                              #domain=[('move_type', 'in', ['out_invoice','out_refund']),('payment_state', 'not in', ['paid']),('state','=',('posted')),('amount_residual','>',0.0)]) 


    # Incluye SO Nada que facturar (no) y Por facturar (to invoice)
    balance_sale_order_ids = fields.One2many('sale.order', 'partner_id', string=_('Notas de Venta'), compute='_compute_so_list')
#                              domain=[('amount_total','>',0.0),('state','=','sale'),('invoice_status','!=','invoiced')]) 

                              #domain=[('amount_total','>',0.0),'|',('state', '=', 'draft'),'&',('state','=','sale'),('invoice_status','!=','invoiced')]) 
                              #domain=[('amount_total','>',0.0),'|',('state', '=', 'draft'),'&',('state','=','sale'),('invoice_status','=','to invoice')]) 

    #JCR. Calcula pagos desde modelo account.payment
    balance_payment_ids = fields.One2many('account.payment', 'partner_id', string=_('Pagos no Conciliados'), compute='_compute_payment_list')
                              #domain=[('is_reconciled', '=', False),('state','=','posted'),('partner_id','=',)]) 
                              #domain=['&',('is_reconciled', '=', False),'|',('move_type','=','in_receipt'),('move_type','=','out_receipt'),('state','=','posted')]) 
                              #domain=['&',('is_reconciled', '=', False),('payment_type','=','inbound'),('state','=','posted')]) 

    # ==== Pagos ====
    res_partner_credits = fields.Text(string="Pagos",groups="account.group_account_invoice,account.group_account_readonly",
        compute='_compute_res_partner_credits')

    @api.depends('credit_amount','invoice_amount','payment_amount')
    def _compute_credito_usado(self):
        self.credito_usado = self.invoice_amount + self.credit_amount - self.payment_amount



    @api.depends('balance_invoice_ids')
    def _compute_invoice_amount(self):
        amount = 0.0
        for pago in self.balance_invoice_ids:
            amount += pago.amount_total_signed
        self.invoice_amount = amount


    @api.depends('balance_payment_ids')
    def _compute_payment_amount(self):
        amount = 0.0
        for pago in self.balance_payment_ids:
            amount += pago.amount_company_currency_signed
        self.payment_amount = amount


    def _compute_invoice_list(self):
        
        #if self.is_company:
        if self.company_type == 'company':
            partner = self.id
        else:
            partner = self.parent_id.id

        lines = self.env['account.move'].search([('partner_id','=',partner),('move_type', 'in', ['out_invoice','out_refund']),('payment_state', 'not in', ['paid']),('state','=',('posted'))]) 

#        for line in lines:
#            reconciled_payments = line._get_reconciled_payments()
#            for a in reconciled_payments:
#                _logger.info(a)

#                    if not reconciled_payments or all(payment.is_matched for payment in reconciled_payments):
#                        new_pmt_state = 'paid'

        self.balance_invoice_ids = lines

    def _compute_payment_list(self):
        Payments = self.env['account.payment']

        if self.is_company:
            partner = self.id
        else:
            partner = self.parent_id.id

        self.balance_payment_ids = Payments.search([('partner_id', '=', partner),('state','=','posted'),('is_reconciled', '=', False),('payment_type','=','inbound')])



    def _compute_so_list(self):
        #self.balance_sale_order_ids
        sale_orders = self.env['sale.order']

        if self.is_company:
            partner = self.id
        else:
            partner = self.parent_id.id

        uno = sale_orders.search([('partner_id', '=', partner),
            ('amount_total','>',0.0),('state', '=', 'sale'),('invoice_status','=','to invoice')])

        dos = sale_orders.search([('partner_id', '=', partner),('amount_total','>',0.0),
                ('state', '=', 'sale'),('invoice_status','=','invoiced')])
        for order in dos:
            flag = False
            for inv in order.invoice_ids:
                if inv.state == 'draft':
                    flag = True
            if flag == True:
                tres = sale_orders.search([('partner_id', '=', partner),('id','=',order.id)])
                uno = uno | tres
        self.balance_sale_order_ids = uno


    @api.depends('balance_sale_order_ids')
    def _compute_credit_amount(self):
        credit_for_orders = 0.0
        if self.balance_sale_order_ids:
            for order in self.balance_sale_order_ids:
                #_logger.info('CREDIT order %s',order.name)
                credit_for_orders += order.amount_total

        self.credit_amount = credit_for_orders

        #if self.credit:
        #    total_receivable = self.credit
        #else:
        #    total_receivable = self.parent_id.credit
#
#        self.used_credit = self.credit_amount + total_receivable
        self.used_credit = 0.0


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
        else:
            payments_widget_vals['outstanding'] = False
        payments_widget_vals['total'] = total

        _logger.info(payments_widget_vals)
        self.res_partner_credits = json.dumps(payments_widget_vals)

