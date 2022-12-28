from odoo import api, fields, models, tools, _

import logging

_logger = logging.getLogger(__name__)


class CotizadorInsumo(models.TransientModel):
    _name = 'cotizador.insumo'
    _description = 'Insumos'
    _order = 'id'

    select_id          = fields.Many2one('select.products', ondelete="cascade")
    name               = fields.Char('Nombre', default="/")

    product_product_id = fields.Many2one('product.product', string="Producto")

    @api.model
    def _default_currency_id(self):
        return self.env.user.company_id.currency_id.id

    cost_currency_id   = fields.Many2one('res.currency', 'Moneda de costo', default=_default_currency_id)
    uom_id             = fields.Many2one('uom.uom', string='Unidad de Consumo')
    cantidad           = fields.Float("Cantidad", digits=(10,3))
    costo_unitario     = fields.Float(string='Costo Unitario')
    costo_consumo      = fields.Float(string='Costo Total')
    merma              = fields.Float(string="Merma (%)", default=0.0)
    incluido_en_ldm    = fields.Boolean(string="En LdM?", default=False)
    flag_adicional     = fields.Boolean(string="Item agregado por el usuario", default=True)

    @api.onchange('cantidad', 'costo_unitario')
    def _onchange_cantidad(self):
        self.costo_consumo = self.cantidad * self.costo_unitario

