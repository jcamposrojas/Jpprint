# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import SUPERUSER_ID
from odoo import models,fields,api

class wizard_credit_limit(models.TransientModel):
    _name = "wizard_custom_credit"
    
    @api.depends('total_receivable')
    def _bi_compute_exceeded_amount(self):
        self.sale_name = self.env.context.get('sale_order_name')
        self.customer_name = self.env.context.get('default_partner_id_name')
        self.current_quotation = self.env.context.get('amount_total')
        self.customer_credit_limit = self.env.context.get('credit_limit')
        self.total_receivable = self.env.context.get('total_recievable')
        #JCR
        self.due_before = self.total_receivable + self.current_quotation
        self.so_credit  = self.env.context.get('so_credit')
        
    
    @api.depends('total_receivable', 'customer_credit_limit')
    def _compute_exceeded_amount(self):
        self.exceeded_amount = self.env.context.get('so_credit') + self.total_receivable - self.customer_credit_limit + self.current_quotation 
        
    
    customer_name = fields.Char(compute='_bi_compute_exceeded_amount', string="Name :")
    sale_name = fields.Char(string="Current Order :", readonly=True)
    customer_credit_limit = fields.Float(string="Credit Limit", readonly=True)
    credit_on_hold = fields.Boolean(string="Bloquear Cliente", readonly=True)
    total_receivable = fields.Float(string="Total Receivable", readonly=True)
    current_quotation = fields.Float(string="Current Quotation", readonly=True)
    due_before = fields.Float(string="Due after this Quotation", readonly=True)
    exceeded_amount = fields.Float(string="Exceeded Amount", compute="_compute_exceeded_amount")
    #JCR
    currency_id = fields.Many2one('res.currency', string='Credit Currency', help="", tracking=True)
    so_credit   = fields.Monetary(string='Total Nota de Venta', readonly=True)
    
    
        
    def confirm_sale(self):
        su_id =self.env['res.partner'].browse(SUPERUSER_ID)
        partner_id = self.env['res.partner'].search([('name','=',self.customer_name)])
        partner_id.write({'credit_limit' : self.customer_credit_limit})
        context = self._context
        active_ids = context.get('active_ids')
        sale_id = self.env['sale.order'].sudo().browse(self._context.get('active_ids'))
        for partner in partner_id:
            if partner:
                template_id = self.env['ir.model.data'].sudo()._xmlid_lookup('bi_customer_limit.email_template_edi_credit_limit')[2]
                email_template_obj = self.env['mail.template'].sudo().browse(template_id)
                if template_id:
                    values = email_template_obj.generate_email(active_ids[0], ['subject', 'body_html', 'email_from', 'email_to', 'partner_to', 'email_cc', 'reply_to', 'scheduled_date'])
                    email_values = {}
                    email_values['email_to'] = su_id.email
                    email_values['email_from'] = partner.email
                    email_values['subject'] = values.get('subject') or ''
                    email_values['body_html'] = values.get('body_html') or ''
                    email_values['res_id'] = False
                    email_values['author_id'] = self.env['res.users'].browse(self._uid).partner_id.id

                    msg_id = self.env['mail.mail'].sudo().create(email_values)
                    if msg_id:
                        self.env['mail.mail'].sudo().send([msg_id])

#JCR
#        sale_id.write({
#            'is_confirm' : True 
#        })

        # JCR. No se debe dejar seguir con la confirmacion
        #sale_id.action_confirm()                           
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

    
     
