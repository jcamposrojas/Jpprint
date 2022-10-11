from odoo import api, fields, models, tools, _


class CotizadorAdicional(models.Model):
    _name = 'cotizador.adicional'
    _description = 'Entradas Adicionales'

    producto_ids       = fields.Many2many(comodel_name="cotizador.producto",string="Productos")
    name               = fields.Char('Descripción', required=True)
    product_product_id = fields.Many2one('product.product', string="Producto/Insumo")
    uom_id             = fields.Many2one('uom.uom', string='Unidad de Consumo', related='product_product_id.uom_id')
#    rendimiento        = fields.Float(string='Rendimiento',  default=1.0)
    standard_price     = fields.Float(string='Costo', related='product_product_id.standard_price')
    cost_currency_id   = fields.Many2one('res.currency', 'Moneda de costo', related="product_product_id.cost_currency_id")
    incluido_en_ldm    = fields.Boolean(string="En LdM?", default=True)


