from odoo import api, fields, models, tools, _


class CotizadorTroquel(models.Model):
    _name = 'cotizador.troquel'
    _description = 'Troqueles'
    _order = 'id'

    name     = fields.Char('Descripción', required=True)
    z        = fields.Integer(string='# Dientes troquel (z)')
    tipo     = fields.Selection([
        ('digital','Digital'),('laser','Laser'),('solido','Sólido'),('flexible','Flexible')
        ], default='solido')
    unidades = fields.Integer('Cantidad', required=True)

