# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _, tools


class CotizadorProductoTtr(models.Model):
    _name = 'producto_ttr'

    producto_id        = fields.Many2one('cotizador.producto', 'Producto', required=True)

    #------- Producto ---------
    product_product_id = fields.Many2one('product.product', string='Cinta TTR')
    cost_currency_id   = fields.Many2one('res.currency', 'Moneda de costo',
                         related="product_product_id.cost_currency_id")
    cost_currency_symbol = fields.Char(string='Símbolo moneda', related="product_product_id.cost_currency_id.symbol")
    standard_price     = fields.Float(string='Costo de producto', related='product_product_id.standard_price')


    #------- Campos largo ancho ---------
    # En UoM original
    largo = fields.Integer(string='Largo', related='product_product_id.largo')
    ancho = fields.Integer(string='Ancho', related='product_product_id.ancho')

    # UoM
    largo_uom_id = fields.Many2one('uom.uom', string='Uom largo', related='product_product_id.largo_uom_id')
    ancho_uom_id = fields.Many2one('uom.uom', string='Uom ancho', related='product_product_id.ancho_uom_id')

    # En mm
    largo_mm = fields.Integer(string='Largo en mm', compute='_compute_values')
    ancho_mm = fields.Integer(string='Ancho en mm', compute='_compute_values')


    #------- Area en m(2)--------
    area  = fields.Float(string='Area', compute='_compute_values')
    def _get_default_area_uom_id(self):
        return self.env.ref('uom.uom_square_meter').id
    area_uom_id = fields.Many2one('uom.uom', string='Uom Area', default=_get_default_area_uom_id, readonly=True)


    incluido_en_ldm    = fields.Boolean(string="En LdM?", default=True, readonly=True)
    merma              = fields.Float(string="Merma (%)", default=0.0)

    @api.depends('largo', 'ancho', 'largo_uom_id', 'ancho_uom_id')
    def _compute_values(self):
        for rec in self:
            # Largo
            largo_m      = rec.largo_uom_id._compute_quantity(rec.largo,self.env.ref('uom.product_uom_meter'))
            rec.largo_mm = rec.largo_uom_id._compute_quantity(rec.largo,self.env.ref('uom.product_uom_millimeter'))

            # Ancho
            ancho_m      = rec.ancho_uom_id._compute_quantity(rec.ancho,self.env.ref('uom.product_uom_meter'))
            rec.ancho_mm = rec.ancho_uom_id._compute_quantity(rec.ancho,self.env.ref('uom.product_uom_millimeter'))

            # Area en m(2)
            rec.area = largo_m * ancho_m

