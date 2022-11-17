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


class sale_order(models.Model):
    _inherit = "sale.order"
    
    #credit_limit_id   = fields.Monetary(string="Credit Limit", currency_field='currency_id')
    total_receivable  = fields.Monetary(string="Total Receivable", compute="_compute_total_receivable", currency_field='currency_id')

    exceeded_amount   = fields.Monetary(string="Exceeded Amount", currency_field='currency_id')
    sale_url          = fields.Char(string="url", compute="_compute_total_receivable")
    customer_due_amt  = fields.Monetary(related='partner_id.credit', string='Customer Due Amount',
                            currency_field='currency_id',
                            depends=['partner_id'])
    credit_limit      = fields.Monetary(related='partner_id.credit_limit', string='Crédito Usado',
                            currency_field='currency_id',
                            depends=['partner_id'])
    used_credit       = fields.Monetary(related='partner_id.used_credit', string='Crédito Usado',
                            currency_field='currency_id',
                            depends=['partner_id'])

    is_confirm = fields.Boolean(string="Is Confirm",default=False, copy=False)
    is_warning = fields.Boolean(string="Is Warning",default=False, copy=False)
    # Nuevos
    invoice_amount = fields.Monetary(related='partner_id.invoice_amount', string='Monto por Facturas',
                            currency_field='currency_id', depends=['partner_id'])
    credito_usado  = fields.Monetary(related='partner_id.credito_usado', string='Crédito Usado',
                            currency_field='currency_id', depends=['partner_id'])
    

    def _compute_total_receivable(self):
        for order in self:

            if order.partner_id.credit:
                order.update({'total_receivable' : self.partner_id.credit})
            if not order.partner_id.credit:
                order.update({'total_receivable' : self.partner_id.parent_id.credit})

            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            static_url = "/web"
            view_id = "?db=%s#id=%s" % (self._cr.dbname, self.id)
            view_type = "&view_type=form&model=sale.order"
            sale_url_id = str(base_url) + static_url + view_id + view_type

            order.update({
                'sale_url' : sale_url_id
            })

    @api.model
    def create(self, vals):
        if self.state == False:
            return super(sale_order, self).create(vals)

        if self._validate_credit(vals) == False:
            return False 
             
        return super(sale_order, self).create(vals)

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if not self.partner_id:
            self.update({
                'partner_invoice_id' : False,
                'partner_shipping_id': False,
                'payment_term_id': False,
                'fiscal_position_id': False,
            })
            return

        if not self.partner_id.credit:
            self.partner_id.credit = self.partner_id.parent_id.credit
            
        addr = self.partner_id.address_get(['delivery', 'invoice'])

        vals = {
            'pricelist_id' : self.partner_id.property_product_pricelist and self.partner_id.property_product_pricelist.id or False,
            'payment_term_id' : self.partner_id.property_payment_term_id and self.partner_id.property_payment_term_id.id or False,
            'partner_invoice_id': addr['invoice'],
            'partner_shipping_id': addr['delivery'],
            #'credit_limit_id': self.partner_id.credit_limit,
            'credit_limit': self.credit_limit,
            'total_receivable': self.partner_id.credit,
        }

        if self.partner_id.user_id:
            vals['user_id'] = self.partner_id.user_id.id
        if self.partner_id.team_id:
            vals['team_id'] = self.partner_id.team_id.id
        
        if self.partner_id.is_credit_limit == True:
            if self.partner_id.credit > self.partner_id.credit_limit:
                self.is_warning = True
            else:
                self.is_warning = False
        else:
            self.is_warning = False
        self.update(vals)


    def _validate_credit(self,vals):
        partner = False
        if 'partner_id' in vals:
            partner = self.env['res.partner'].browse(vals['partner_id'])

        # Validate Put on Hold
        if partner.credit_on_hold is True:
           #raise UserError(_('You have been put on hold due to exceeding your credit limit. Please contact administration for further guidance. \n Thank You'))
            raise UserError(_('El Cliente ha sido bloqueado por exceder su Límite de Crédito. Por favor contacte al Administrador.\nGracias!'))
            return False

        if partner.is_credit_limit == True:
            if partner.credit_limit <= 0.0:
               raise UserError(_('Usuario con crédito 0, favor contactar a administración.\nGracias'))
               return False

            if partner.blocking_limit != 0.0:
                # Facturado NO pagado
                if partner.blocking_limit < partner.invoice_amount:
                    raise UserError(_('The Customer is in blocking stage and has to pay ' + str(partner.invoice_amount)))

            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            #amount_total = vals.get('amount_total')

            _logger.info(' 123 ')
            _logger.info(self.state)
            _logger.info(vals)
            amount_total = 0.0
            for line in vals.get('order_line'):
                price_unit      = line[2]['price_unit']
                product_uom_qty = line[2]['product_uom_qty']
                tax_id          = line[2]['tax_id'][0][2][0]
                tax             = self.env['account.tax'].browse(tax_id)
                tax_amount      = tax['amount']
                discount        = line[2]['discount']

                price    = price_unit * (1 - (discount or 0.0) / 100.0)
                subtotal = price * product_uom_qty
                amount_total += subtotal

            if amount_total > 0.0:
                amount_total = amount_total * (1+(tax_amount or 0.0) / 100.0)
                amount_total = round(amount_total, precision)

            exceeded_amount = amount_total + partner.credito_usado - partner.credit_limit

            if exceeded_amount > 0:
                raise UserError(_('Lo sentimos, se ha excedido el Límite de Crédito del cliente\n \
                       Límite de Crédito     : %s\n \
                       Credito por NV        : %s\n \
                       Total deuda facturada : %s\n \
                       Cantidad Excedida     : %s')%(partner.credit_limit,partner.credit_amount,partner.invoice_amount,exceeded_amount))
                #raise UserError(_('Lo sentimos, se ha excedido el Límite de Crédito del cliente\n \
                #       Límite de Crédito     : %s\n \
                #       Credito por NV        : %s\n \
                #       Total deuda facturada : %s\n \
                #       Cantidad Excedida     : %s')%(partner.credit_limit,partner.so_credit,total_receivable,amount_total,exceeded_amount))
                return False
        return True

    def action_confirm(self):
        partner = self.partner_id

        _logger.info(' STATE ')
        _logger.info(self.state)
        # Validate Put on Hold
        if partner.credit_on_hold is True:
            raise UserError(_('El Cliente ha sido bloqueado por exceder su Límite de Crédito. Por favor contacte al Administrador.\nGracias!'))
            return False

        if partner.is_credit_limit == False:
            return super(sale_order, self).action_confirm()
        else:
            if partner.credit_limit <= 0.0:
                raise UserError(_('Usuario con crédito 0, favor contactar a administración.\nGracias'))
                return False

            # Incluye pagos
            if partner.credit:
                total_receivable = partner.credit
            else:
                if not partner.parent_id:
                    total_receivable = partner.parent_id.credit

            if partner.blocking_limit != 0.0:
                # Facturado NO pagado
                if partner.blocking_limit < total_receivable:
                    raise UserError(_('The Customer is in blocking stage and has to pay ' + str(total_receivable)))

            exceeded_amount = self.credito_usado - partner.credit_limit + self.amount_total

            if exceeded_amount > 0:
                raise UserError(_('Sorry, your Credit limit has exceeded. You can still confirm\n \
                               Order but a mail will be sent to administration department.\n \
                               Credit Limit     : %s\n \
                               Credit for SO    : %s\n \
                               Total Receivable : %s\n \
                               Current SO       : %s\n \
                               Exceeded Amount  : %s')%(partner.credit_limit,\
                                   partner.credit_amount,\
                                   partner.invoice_amount,self.amount_total,exceeded_amount))
                return False
            return super(sale_order, self).action_confirm()
