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
    name               = fields.Char(string='Nombre')

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
    gap                = fields.Float(string='Gap')
    z                  = fields.Integer(string='Z')
    tipo_troquel       = fields.Selection(TIPO_TROQUEL,string='tipo_troquel')

    # UoM
#    largo_uom_id = fields.Many2one('uom.uom', string='Uom largo', related='product_product_id.largo_uom_id')
#    ancho_uom_id = fields.Many2one('uom.uom', string='Uom ancho', related='product_product_id.ancho_uom_id')

    # En mm
#    largo_mm = fields.Integer(string='Largo en mm', compute='_compute_values')
#    ancho_mm = fields.Integer(string='Ancho en mm', compute='_compute_values')

    def name_get(self):
        lst = []
        for rec in self:
            lst.append((rec.id,"%3s X %3s" % (rec.largo,rec.ancho)))
        return lst

