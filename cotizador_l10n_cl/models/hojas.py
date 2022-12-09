from odoo import api, fields, models, tools, _
from math import floor


class CotizadorHojas(models.Model):
    _name = 'producto_hojas'
    _description = 'Hojas de Papel'

    name        = fields.Char(string='Nombre', required=True)
#    producto_id = fields.Many2one('cotizador.producto', 'Producto', required=True)

    ancho = fields.Integer(string='Ancho de Hoja', required=True)
    alto  = fields.Integer(string='Alto de Hoja', required=True)

    def _get_default_uom_id(self):
        return self.env.ref('uom.product_uom_millimeter')

    uom_id = fields.Many2one('uom.uom', string='Unidad de Medida', default=_get_default_uom_id)
 
#    codigo  = fields.Char(string='Descripción', compute='_compute_name', store=True)
    _sql_constraints = [
        ('ancho_alto_hoja_uniq', 'unique (ancho,alto)', 'El tamaño de hoja debe ser único.'),
        ]
