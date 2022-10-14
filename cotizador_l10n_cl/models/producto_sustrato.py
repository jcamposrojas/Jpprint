from odoo import api, fields, models, tools, _


class CotizadorSustrato(models.Model):
    _name = 'producto.sustrato'
    _description = 'Relación Producto-Sustratos'
    _order = 'sequence, id'

    producto_id      = fields.Many2one('cotizador.producto', string="Sustrato")
    sustrato_id      = fields.Many2one('cotizador.sustrato', string="Sustrato")

    name             = fields.Char('Descripción', related="sustrato_id.name")
    codigo           = fields.Char('Código', related="sustrato_id.codigo")
    nombre_corto     = fields.Char('Nombre corto', related="sustrato_id.nombre_corto",
            help="Texto incluido en el nombre de producto")
    product_product_id = fields.Many2one('product.product', string="Producto", related="sustrato_id.product_product_id")
    sequence         = fields.Integer( 'Sequence', related="sustrato_id.sequence")

#    def _get_merma_default(self):
#        return self.producto_id.merma_default
#    merma = fields.Float(string="Merma por defecto (%)", default=_get_merma_default)
    merma = fields.Float(string="Merma por defecto (%)", default=0.0)

