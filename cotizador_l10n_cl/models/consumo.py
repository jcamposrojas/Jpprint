# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _, tools


class CotizadorConsumoProducto(models.Model):
    _name = 'cotizador.consumo'
    #_order = 'sequence, id'
    _order = 'id'

    producto_id        = fields.Many2one('cotizador.producto', 'Producto', required=True)
    product_product_id = fields.Many2one('product.product', string="Producto/Insumo")
    # UOM de producto
    uom_id             = fields.Many2one('uom.uom', string='Unidad de Medida', related='product_product_id.uom_id')
    uom_category_id    = fields.Many2one('uom.category',string='Categoría de Medida',related='product_product_id.uom_id.category_id')

    # UOM de consumo
    def _get_default_product_uom_id(self):
        return self.uom_id.id

    consumo_uom_id     = fields.Many2one('uom.uom', string='Unidad de Consumo', default=_get_default_product_uom_id)
    standard_price     = fields.Float(string='Costo de producto', related='product_product_id.standard_price')
    cost_currency_id   = fields.Many2one('res.currency', 'Moneda de costo', related="product_product_id.cost_currency_id")
    cantidad           = fields.Float(string='Cantidad', default=0.0, digits=(20,10))
    costo_consumo      = fields.Float(string='Costo', compute='_compute_costo_consumo', digits=(20,10))
    incluido_en_ldm    = fields.Boolean(string="En LdM?", default=True)

    @api.depends('consumo_uom_id','standard_price','cantidad')
    def _compute_costo_consumo(self):
        for rec in self:
            rec.costo_consumo = rec.standard_price * rec.consumo_uom_id.factor_inv * rec.cantidad

