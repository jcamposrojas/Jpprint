# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _, tools


class CotizadorProductoHomologo(models.Model):
    _name = 'producto_homologo'
    #_order = 'id'

    producto_id        = fields.Many2one('cotizador.producto', 'Producto', required=True)

    # Producto
    product_product_id = fields.Many2one('product.product', string="Producto/Insumo")

    # UOM de producto
    uom_id             = fields.Many2one('uom.uom', string='Unidad de Medida', related='product_product_id.uom_id')
    uom_category_id    = fields.Many2one('uom.category',string='Categoría de Medida',related='product_product_id.uom_id.category_id')

    # UOM de consumo
    consumo_uom_id     = fields.Many2one('uom.uom', string='Unidad de Consumo')
    cantidad_homologo  = fields.Float(string='Cantidad Homologada')

    standard_price     = fields.Float(string='Costo de producto', related='product_product_id.standard_price')
    cost_currency_id   = fields.Many2one('res.currency', 'Moneda de costo', related="product_product_id.cost_currency_id")
    incluido_en_ldm    = fields.Boolean(string="En LdM?", default=True, readonly=True)
    merma              = fields.Float(string="Merma (%)", default=0.0)
