from odoo import api, fields, models, tools, _


class CotizadorAdhesivo(models.Model):
    _name = 'cotizador.adhesivo'
    _description = 'Adhesivo'

    codigo       = fields.Char('Código', required=True)
    name         = fields.Char('Descripción', required=True)
    nombre_corto = fields.Char('Nombre corto', required=True, help="Texto incluido en el nombre de producto")

