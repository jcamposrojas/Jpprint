from odoo import api, fields, models, tools, _


class CotizadorInsumo(models.TransientModel):
    _name = 'cotizador.insumo'
    _description = 'Insumos'
    _order = 'id'

    select_id          = fields.Many2one('select.products')
    name               = fields.Char('Nombre', default="/")

    product_product_id = fields.Many2one('product.product', string="Producto")
    cost_currency_id   = fields.Many2one('res.currency', 'Moneda de costo', related="product_product_id.cost_currency_id")
    uom_id             = fields.Many2one('uom.uom', string='Unidad de Consumo')
    cantidad           = fields.Float("Cantidad")
    costo_consumo      = fields.Float(string='Costo')
    merma              = fields.Float(string="Merma (%)", default=0.0)
    incluido_en_ldm    = fields.Boolean(string="En LdM?")

#    @api.model
#    def create(self,vals):
#        for rec in self:
#            if rec.product_product_id:
#                vals['name'] = rec.product_product_id.name
#            return super(CotizadorInsumo,self).create(vals)



