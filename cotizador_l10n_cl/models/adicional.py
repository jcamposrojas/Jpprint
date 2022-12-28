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

class CotizadorAdicional(models.Model):
    _name = 'cotizador.adicional'
    _description = 'Entradas Adicionales'

    company_id       = fields.Many2one('res.company', default=lambda self: self.env.company)
    cost_currency_id = fields.Many2one('res.currency', readonly=True, related='company_id.currency_id')
    producto_id      = fields.Many2one("cotizador.producto", string="Producto")

    # UOM de producto
    uom_id           = fields.Many2one('uom.uom', string='Unidad de Consumo')
    uom_category_id  = fields.Many2one('uom.category',string='Categoría de Medida')

    uom_id_de_consumo = fields.Many2one('uom.uom', string='UoM de consumo')


    name             = fields.Char('Descripción', required=True)
    standard_price   = fields.Float(string='Costo Producto')
    cantidad         = fields.Float(string="Cantidad", default=1.0)
    costo_unitario_consumo = fields.Float(string='Costo unitario consumo')
    incluido_en_ldm  = fields.Boolean(string="En LdM?", default=False)

    # Adicionales
    product_product_id = fields.Many2one('product.product', string="Producto/Insumo")
    add_data           = fields.Boolean('Agrega campo dato?', default=False)
    tipo_data          = fields.Selection([('t','Texto'),('s','Selección')], default='t')

    data               = fields.Char('Dato adicional',
                         help='Este campo se agrega a name si es seleccionado')
    tipo_calculo       = fields.Selection(TIPOS_CALCULO,
                         string="Tipo consumo", default='m2', required=True,
                         help="Indica si el consumo es fijo, por metro o metro cuadrado")
    descripcion        = fields.Char(string='Descripción')

    @api.onchange('product_product_id')
    def _onchange_product_id(self):
        if self.product_product_id:
            self.name              = self.product_product_id.name
            self.standard_price    = self.product_product_id.standard_price
            self.incluido_en_ldm   = True
            self.uom_id            = self.product_product_id.uom_id
            self.uom_category_id   = self.product_product_id.uom_id.category_id
            self.uom_id_de_consumo = self.product_product_id.uom_id

    @api.onchange('uom_id', 'uom_id_de_consumo','standard_price')
    def _onchange_costo_unitario_consumo(self):
        for rec in self:
            # Lleva a uom de referencia
            if rec.uom_id.uom_type == 'reference':
                factor = 1
            elif rec.uom_id.uom_type == 'bigger':
                factor = rec.uom_id.factor_inv
            else:
                factor = rec.uom_id.factor

            # Calcula en uom de consumo
            if rec.uom_id_de_consumo.uom_type == 'reference':
                factor2 = 1
            elif rec.uom_id_de_consumo.uom_type == 'bigger':
                factor2 = rec.uom_id_de_consumo.factor
            else:
                factor2 = rec.uom_id_de_consumo.factor_inv

            factor = factor * factor2
            rec.costo_unitario_consumo = rec.standard_price * factor


#        else:
#            self.name              = ''
#            self.standard_price    = None
#            self.incluido_en_ldm   = False
#            self.uom_id            = None
#            self.uom_category_id   = None
#            self.uom_id_de_consumo = None

    @api.onchange('cantidad', 'tipo_calculo', 'uom_id_de_consumo')
    def _onchange_descripcion(self):
        if self.cantidad and self.tipo_calculo and self.uom_id_de_consumo:
            self.descripcion = str(self.cantidad) + ' ' + str(self.uom_id_de_consumo.name) + ' ' + dict(self._fields['tipo_calculo'].selection)[self.tipo_calculo]
        else:
            self.descripcion = ''

