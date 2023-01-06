# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _, tools

TIPO_TROQUEL = [
        ('p','PLANO'),
        ('m','MACISO'),
        ('l','LAMINA'),
        ('s','LASER'),
        ]

class TablaTroquel(models.Model):
    _name = 'tabla_troquel'

    producto_id        = fields.Many2one('cotizador.producto', 'Producto', required=True)
    name               = fields.Char(string='Nombre', compute='_compute_name')

    #------- Producto ---------
#    product_product_id = fields.Many2one('product.product', string='Cinta TTR')
#    cost_currency_id   = fields.Many2one('res.currency', 'Moneda de costo',
#                         related="product_product_id.cost_currency_id")
#    cost_currency_symbol = fields.Char(string='Símbolo moneda', related="product_product_id.cost_currency_id.symbol")
#    standard_price     = fields.Float(string='Costo de producto', related='product_product_id.standard_price')


    #------- Campos largo ancho ---------
    # En UoM original
    largo = fields.Integer(string='Largo', required=True)
    ancho = fields.Integer(string='Ancho', required=True)
    etiquetas_al_ancho = fields.Integer(string='Etiquetas al Ancho')
    gap                = fields.Float(string='Gap', compute='_compute_gap', digits=(10, 3))
    gap_minimo         = fields.Float(string='Gap Mímino', default=3.0)
    z                  = fields.Integer(string='Z')
    tipo_troquel       = fields.Selection(TIPO_TROQUEL,string='tipo_troquel')

    # UoM
#    largo_uom_id = fields.Many2one('uom.uom', string='Uom largo', related='product_product_id.largo_uom_id')
#    ancho_uom_id = fields.Many2one('uom.uom', string='Uom ancho', related='product_product_id.ancho_uom_id')

    # En mm
#    largo_mm = fields.Integer(string='Largo en mm', compute='_compute_values')
#    ancho_mm = fields.Integer(string='Ancho en mm', compute='_compute_values')

    @api.depends('largo', 'ancho')
    def _compute_name(self):
        for rec in self:
            rec.name = "%3s X %3s" % (rec.largo,rec.ancho)
#        lst = []
#        for rec in self:
#            lst.append((rec.id,"%3s X %3s" % (rec.largo,rec.ancho)))
#        return lst

    @api.depends('z', 'largo')
    def _compute_gap(self):
        for rec in self:
            if rec.z > 0 and rec.largo > 0:
                i = 1
                c_calc = 0
                c_calc_ant = 0
                perimetro = rec.z * 3.175
                while True:
                    c_calc_ant = c_calc
                    c_calc = perimetro / i  - rec.largo

                    if c_calc <= rec.gap_minimo:
                        break
                    i = i + 1
                rec.gap = perimetro / (i-1) - rec.largo
            else:
                rec.gap = 0


