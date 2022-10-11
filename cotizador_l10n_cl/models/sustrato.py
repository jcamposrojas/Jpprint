from odoo import api, fields, models, tools, _


class CotizadorSustrato(models.Model):
    _name = 'cotizador.sustrato'
    _description = 'Sustratos'
    _order = 'sequence, id'

    codigo           = fields.Char('Código', required=True)
    name             = fields.Char('Descripción', required=True)
    nombre_corto     = fields.Char('Nombre corto', required=True, help="Texto incluido en el nombre de producto")
    product_product_id = fields.Many2one('product.product', string="Producto")
    sequence         = fields.Integer( 'Sequence', default=100)
    uom_id           = fields.Many2one('uom.uom', string='Unidad de Medida', related='product_product_id.uom_id')
    standard_price   = fields.Float(string='Costo', related='product_product_id.standard_price')
    cost_currency_id = fields.Many2one('res.currency', 'Moneda de costo', related="product_product_id.cost_currency_id")

