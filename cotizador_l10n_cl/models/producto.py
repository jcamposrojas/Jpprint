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
    use_cuatricomia       = fields.Boolean(string='Usa Cuatricomia', default=False)
    use_aisa              = fields.Boolean(string='Usa AISA', default=False)
    use_adhesivo          = fields.Boolean(string='Usa Adhesivo', default=True)

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

    #---------------- Cuatricomia (Flexo) -------------------
    barniz        = fields.Many2one('producto_generico', string='Barniz',
                    context="{'producto_id':id}", domain="[('producto_id','=',id)]")
    color_cyan    = fields.Many2one('producto_generico', string='Color Cyan',
                    context="{'producto_id':id}", domain="[('producto_id','=',id)]")
    color_black   = fields.Many2one('producto_generico', string='Color Black',
                    context="{'producto_id':id}", domain="[('producto_id','=',id)]")
    color_yellow  = fields.Many2one('producto_generico', string='Color Yellow',
                    context="{'producto_id':id}", domain="[('producto_id','=',id)]")
    color_magenta = fields.Many2one('producto_generico', string='Color Magenta',
                    context="{'producto_id':id}", domain="[('producto_id','=',id)]")
    color1        = fields.Many2one('producto_generico', string='Color 1',
                    context="{'producto_id':id}", domain="[('producto_id','=',id)]")
    color2        = fields.Many2one('producto_generico', string='Color 2',
                    context="{'producto_id':id}", domain="[('producto_id','=',id)]")
    color3        = fields.Many2one('producto_generico', string='Color 3',
                    context="{'producto_id':id}", domain="[('producto_id','=',id)]")
    color4        = fields.Many2one('producto_generico', string='Color 4',
                    context="{'producto_id':id}", domain="[('producto_id','=',id)]")

   # m2_ids = fields.One2many('tabla_m2', 'producto_id', string='Metros Cuadrados')
    tarifa_ids     = fields.One2many('tarifa', 'producto_id', string='Tarifa')
    tarifa_txt_ids = fields.Html(string="Texto Tarifa", compute='_get_html_tarifas')

#    tarifa_txt_ids = fields.Text(string='Tarifas', compute="_compute_tarifa_text")

#    @api.depends('tarifa_ids')
#    def _compute_tarifa_text(self):
#        txt = ""
#        m2 = 0
#        list_parametros = {'content':[]}
#
#        for tarifa in self.tarifa_ids:
#            if tarifa.m2 != m2:
#                linea = {'m2' : m2,
#                        '' :}
#                m2 = tarifa.m2


    #Cliches
    def _domain_category_id_cliche(self):
        domain = "[('category_id','=',%s)]" % (self.env.ref('uom.uom_categ_surface').id)
        return domain

    cliche_uom_id_de_consumo      = fields.Many2one('uom.uom', domain=_domain_category_id_cliche, string='UoM de consumo')
    cliche_costo_unitario_consumo = fields.Float(string='Costo unitario consumo')


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

    def action_import_tarifa(self):
        return {
            'name': "Importar Tarifa",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'import.tarifa',
            'view_id': self.env.ref('cotizador_l10n_cl.wizard_import_tarifa').id,
            'target': 'new',
            }

    @api.depends('tarifa_ids')
    def _get_html_tarifas(self):
        tarifas = self.tarifa_ids
        if len(tarifas) == 0:
            self.tarifa_txt_ids = ''
            return
            
        m2 = -1
        matriz = {}
        for item in tarifas:
            if item.m2 != m2:
                m2 = item.m2
                matriz[m2] = {}
                matriz[m2][item.sustrato_id.id] = item.porcentaje
            else:
                matriz[m2][item.sustrato_id.id] = item.porcentaje

        html = "<table>"

        html = html + "<tr style='border-bottom: 1px solid black;'>"
        html = html + "<td style='width:60px;border-right: 1px solid black;'><strong>M2</strong></td>"
        first_m2 = list(matriz.keys())[0]
        for k in matriz[first_m2]:
            sus = self.env['cotizador.sustrato'].search([('id','=',k)])
            if sus:
                sus_codigo = sus.codigo
            else:
                sus_codigo = ""
            html = html + "<td style='width:60px'><strong>" + sus.codigo + "</strong></td>"
        html = html + "</tr>"

        i = 0
        for k in matriz.keys():
            if i % 2 == 1:
                html = html + "<tr style='background-color:#f6f7fa'><td style='border-right: 1px solid black'>" + str(k) + "</td>"
            else:
                html = html + "<tr><td style='border-right: 1px solid black'>" + str(k) + "</td>"
            for v in matriz[k].keys():
                html = html + "<td>" + str(matriz[k][v]) + "% </td>"
            i = i + 1
            html = html + "</tr>"

        html = html + "</table>"

        self.tarifa_txt_ids = html

