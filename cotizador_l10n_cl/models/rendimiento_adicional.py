# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _, tools


class CotizadorRendimientoAdicional(models.Model):
    _name = 'rendimiento.adicional'
    #_order = 'sequence, id'
    _order = 'id'

    producto_id      = fields.Many2one('cotizador.producto', 'Producto', required=True)

    adicional_id     = fields.Many2one('cotizador.adicional', 'Entrada Adicional', required=True)
    standard_price_adicional = fields.Float(string='Costo', related='adicional_id.product_product_id.standard_price')

    rendimiento      = fields.Float(string='Rendimiento', default=1.0)
    producto_uom_id  = fields.Many2one('uom.uom', string='Unidad de Producto', related='producto_id.uom_id')
    adicional_uom_id = fields.Many2one('uom.uom', string='Unidad de Consumo', related='adicional_id.uom_id')


