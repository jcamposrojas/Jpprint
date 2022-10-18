from odoo import api, fields, models, tools, _


class CotizadorAdicional(models.Model):
    _name = 'cotizador.adicional'
    _description = 'Entradas Adicionales'

    company_id      = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id     = fields.Many2one('res.currency', readonly=True, related='company_id.currency_id')
    producto_id     = fields.Many2one("cotizador.producto",string="Producto")

    name            = fields.Char('Descripción', required=True)
    uom_id          = fields.Many2one('uom.uom', string='Unidad de Consumo')
    standard_price  = fields.Float(string='Costo')
    cantidad        = fields.Float(string="Cantidad", default=1.0)
    incluido_en_ldm = fields.Boolean(string="En LdM?", default=False)






