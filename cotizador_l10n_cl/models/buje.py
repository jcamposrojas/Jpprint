from odoo import api, fields, models, tools, _


class CotizadorAdhesivo(models.Model):
    _name = 'cotizador.buje'
    _description = 'Bujes'

    name               = fields.Char(string='Descripción', required=True)
    longitud           = fields.Float(string='Longitud en metros', required=True)
    product_product_id = fields.Many2one('product.product', string="Producto")
    uom_id             = fields.Many2one('uom.uom', string='Unidad de Medida', related='product_product_id.uom_id')
    standard_price     = fields.Float(string='Costo', related='product_product_id.standard_price')
    cost_currency_id   = fields.Many2one('res.currency', string='Moneda de costo', related="product_product_id.cost_currency_id")


