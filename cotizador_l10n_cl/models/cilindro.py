from odoo import api, fields, models, tools, _

import logging

_logger = logging.getLogger(__name__)


class CotizadorCilindro(models.Model):
    _name = 'cotizador.cilindro'
    _description = 'Cilindros'

    z        = fields.Integer('Z', required=True)
    unidades = fields.Integer('Unidades', required=True)
