from odoo import api, fields, models, tools, _

import logging

_logger = logging.getLogger(__name__)

class CotizadorProducto(models.Model):
    _name = 'cotizador.producto'
    _description = 'Producto genérico'
    _order = 'sequence, id'

    codigo       = fields.Char('Código', required=True)
    name         = fields.Char('Descripción', required=True)
    nombre_corto = fields.Char('Nombre corto', required=True, help="Texto incluido en el nombre de producto")
    category_id  = fields.Many2one('product.category', string="Categoría", required=True)

#    adicional_ids = fields.Many2many(comodel_name="cotizador.adicional",string="Adicionales")
    def _get_default_product_uom_id(self):
        return self.env.ref('uom.uom_square_meter')

    uom_id       = fields.Many2one('uom.uom', string='Unidad de medida Sustrato',
                   default=_get_default_product_uom_id, required=True)
    sequence     = fields.Integer( 'Sequence', default=100)

    producto_sustrato_ids = fields.One2many("producto.sustrato",'producto_id', string="Sustratos")
    consumo_ids           = fields.One2many("cotizador.consumo",'producto_id', string="Consumos")
    operation_ids         = fields.One2many('mrp.routing.workcenter.tmp', 'cotizador_producto_id', string='Operaciones')
    adicional_ids         = fields.One2many("cotizador.adicional",'producto_id', string="Adicionales")
    analytic_account_id   = fields.Many2one('account.analytic.account', 'Cuenta Analítica')

    use_cortes            = fields.Boolean(string='Usa Cortes', default=True,
                            help='Usa Cortes o Tamaños de Hoja')

    corte_default = fields.Many2many('cotizador.cortes', string='Cortes por defecto')

    RF    = fields.Integer(string='RF', help='Ancho borde izquierdo y derecho', default=0)
    SX    = fields.Integer(string='SX', help='Espacio entre Etiquetas en Dirección Ancho', default=0)
    SS    = fields.Integer(string='SS', help='Espacio entre Etiquetas al Centro en Dirección Ancho', default=0)

#    homologo_ids          = fields.One2many('producto_homologo','producto_id', string="Homologados")

    ttr_ids          = fields.One2many('producto_ttr', 'producto_id', string="Cintas TTR")

    hoja_ids         = fields.Many2many('producto_hojas', string="Tamaños de Hoja")

    _sql_constraints = [
        ('codigo_uniq', 'unique (codigo)', 'Campo código debe ser único!.'),
        ]

    def get_cortes(self, sustrato_id):
        for producto_sustrato in self.producto_sustrato_ids:
            #_logger.info(producto_sustrato.sustrato_id.id)
            if producto_sustrato.sustrato_id.id == sustrato_id.id:
                if producto_sustrato.corte_count > 0:
                    return producto_sustrato.corte_ids
                else:
                    return self.corte_default

        return self.corte_default

    def get_best_corte(self, sustrato_id, ancho):
        list_cortes = self.get_cortes(sustrato_id)
        for corte in list_cortes:
            if ancho <= corte.ancho:
                return corte.id, corte.ancho
        return -1, -1

    def get_best_ttr(self, ancho):
        for ttr in self.ttr_ids.sorted('ancho_mm'):
            if ancho <= ttr.ancho:
                return ttr, ttr.ancho
        return None, -1

