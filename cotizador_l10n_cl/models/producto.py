from odoo import api, fields, models, tools, _

import logging

_logger = logging.getLogger(__name__)

TIPOS_CALCULO = [
    ('f','Fijo'),
    ('m','Por metro lineal S/MERMA'),
    ('m+m','Por metro lineal C/MERMA'),
    ('m2','Por metro cuadrado S/MERMA'),
    ('m2+m','Por metro cuadrado C/MERMA'),
]

class CotizadorProducto(models.Model):
    _name = 'cotizador.producto'
    _description = 'Producto genérico'
    _order = 'sequence, id'

    codigo       = fields.Char('Código', required=True)
    name         = fields.Char('Descripción', required=True)
    nombre_corto = fields.Char('Nombre corto', required=True, help="Texto incluido en el nombre de producto")
    category_id  = fields.Many2one('product.category', string="Categoría", required=True)

    default_gap = fields.Float('Gap por defecto', default=0)

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

    use_cortes            = fields.Boolean(string='Usa Anchos de papel', default=True,
                            help='Usa Cortes o Tamaños de Hoja')
    use_bujes             = fields.Boolean(string='Usa Bujes', default=False)
    use_tinta_blanca      = fields.Boolean(string='Usa Tinta Blanca', default=False)
    use_tabla_troquel     = fields.Boolean(string='Usa Tabla Troqueles', default=False)
    use_cinta_ttr         = fields.Boolean(string='Usa Cinta TTR', default=False)

    corte_default = fields.Many2many('cotizador.cortes', string='Ancho por defecto')

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
                return ttr
        return None
        #return None, -1

####################################################################3
#    company_id       = fields.Many2one('res.company', default=lambda self: self.env.company)
#    cost_currency_id = fields.Many2one('res.currency', readonly=True, related='company_id.currency_id')

    # UOM de producto
    product_product_id = fields.Many2one('product.product', string="Producto/Insumo")
    product_uom_id     = fields.Many2one('uom.uom', string='UoM de Producto',
                         related='product_product_id.uom_id')
    product_uom_category_id = fields.Many2one('uom.category', string='Categoría de Medida',
                              related='product_product_id.uom_id.category_id')

    # Consumo
    tblanca_name              = fields.Char('Descripción')
    tblanca_uom_id_de_consumo = fields.Many2one('uom.uom', string='UoM de consumo')
    tblanca_standard_price    = fields.Float(string='Costo Producto')
    tblanca_cantidad          = fields.Float(string="Cantidad", default=1.0)
    tblanca_costo_unitario_consumo = fields.Float(string='Costo unitario consumo')
    tblanca_incluido_en_ldm        = fields.Boolean(string="En LdM?", default=False)
    tblanca_tipo_calculo      = fields.Selection(TIPOS_CALCULO,
                                string="Tipo consumo", default='m2', required=True,
                                help="Indica si el consumo es fijo, por metro o metro cuadrado")


    porcentaje_ids = fields.One2many('tinta_blanca_lines', 'producto_id')

    # Tabla troqueles
    tabla_troquel_ids = fields.One2many('tabla_troquel', 'producto_id', string='Tabla Troqueles')

    @api.onchange('product_uom_id', 'tblanca_uom_id_de_consumo','tblanca_standard_price')
    def _onchange_costo_unitario_consumo(self):
        for rec in self:
            # Lleva a uom de referencia
            if rec.product_uom_id.uom_type == 'reference':
                factor = 1
            elif rec.product_uom_id.uom_type == 'bigger':
                factor = rec.product_uom_id.factor_inv
            else:
                factor = rec.product_uom_id.factor

            # Calcula en uom de consumo
            if rec.tblanca_uom_id_de_consumo.uom_type == 'reference':
                factor2 = 1
            elif rec.tblanca_uom_id_de_consumo.uom_type == 'bigger':
                factor2 = rec.tblanca_uom_id_de_consumo.factor
            else:
                factor2 = rec.tblanca_uom_id_de_consumo.factor_inv

            factor = factor * factor2
            rec.tblanca_costo_unitario_consumo = rec.tblanca_standard_price * factor


    @api.onchange('product_product_id')
    def _onchange_product_id(self):
        if self.product_product_id:
            self.tblanca_name              = self.product_product_id.name
            self.tblanca_standard_price    = self.product_product_id.standard_price
            self.tblanca_incluido_en_ldm   = True
            self.product_uom_id            = self.product_product_id.uom_id
            self.product_uom_category_id   = self.product_product_id.uom_id.category_id
            self.tblanca_uom_id_de_consumo = self.product_product_id.uom_id
#        else:
#            self.name              = ''
#            self.standard_price    = None
#            self.incluido_en_ldm   = False
#            self.uom_id            = None
#            self.uom_category_id   = None
#            self.uom_id_de_consumo = None

