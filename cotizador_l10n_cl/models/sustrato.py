from odoo import api, fields, models, tools, _


class CotizadorSustrato(models.Model):
    _name = 'cotizador.sustrato'
    _description = 'Sustratos'
    _order = 'sequence, id'

    codigo           = fields.Char('Código', required=True)
    name             = fields.Char('Descripción', required=True)
    nombre_corto     = fields.Char('Nombre corto', required=True, help="Texto incluido en el nombre de producto")
    product_product_id = fields.Many2one('product.product', string="Producto")
    sequence         = fields.Integer(string='Sequence', default=100)
    uom_id           = fields.Many2one('uom.uom', string='Unidad de Medida', related='product_product_id.uom_id')
    standard_price   = fields.Float(string='Costo', related='product_product_id.standard_price')
    cost_currency_id = fields.Many2one('res.currency', string='Moneda de costo',
            related="product_product_id.cost_currency_id")

#    corte_ids = fields.Many2many('cotizador.cortes', string='Cortes')

#    def get_max_x_ancho(self,largo,ancho):
#        corte_id          = 0
#        corte_et_al_ancho = -1
#        corte_largo       = 0
#        corte_ancho       = 0

#        for corte in corte_ids:
#            # ID, ET. AL ANCHO, LARGO(AVANCE), ANCHO
#            c_id, c_et_al_ancho, c_largo, c_ancho = corte.get_max_etiquetas_al_ancho(largo,ancho)
#            if c_al_ancho > corte_al_ancho:
#                corte_id       = c_id
#                corte_al_ancho = c_et_al_ancho
#                corte_largo    = c_largo
#                corte_ancho    = c_ancho
#
#        return corte_id, corte_et_al_ancho, corte_largo, corte_ancho



