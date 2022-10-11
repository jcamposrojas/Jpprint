from odoo import api, fields, models, tools, _


class CotizadorProducto(models.Model):
    _name = 'cotizador.producto'
    _description = 'Producto genérico'
    _order = 'sequence, id'

    codigo       = fields.Char('Código', required=True)
    name         = fields.Char('Descripción', required=True)
    nombre_corto = fields.Char('Nombre corto', required=True, help="Texto incluido en el nombre de producto")
    category_id  = fields.Many2one('product.category', string="Categoría", required=True)

    operation_ids = fields.One2many('mrp.routing.workcenter.tmp', 'cotizador_producto_id', string='Operaciones')

    sustratos_ids = fields.Many2many(
        comodel_name="cotizador.sustrato",
        relation="cotizador_producto_sustrato_rel",
        string="Sustratos",
        column1="producto_id",
        column2="sustrato_id",
    )

#    adicional_ids = fields.Many2many(comodel_name="cotizador.adicional",string="Adicionales")
    def _get_default_product_uom_id(self):
        return self.env.ref('uom.uom_square_meter')

    uom_id = fields.Many2one('uom.uom', string='Unidad de medida Sustrato', default=_get_default_product_uom_id, required=True)

    adicional_ids = fields.One2many("rendimiento.adicional",'producto_id', string="Rendimiento de Adicionales")

    sequence     = fields.Integer( 'Sequence', default=100)

    consumo_ids = fields.One2many("cotizador.consumo",'producto_id', string="Consumos")




