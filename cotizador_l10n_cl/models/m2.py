# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from math import floor

from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError


import logging

_logger = logging.getLogger(__name__)

# Tarifas

class MetroCuadrado(models.Model):
    _name = 'tabla_m2'
    _rec_name = 'm2'

    producto_id = fields.Many2one('cotizador.producto', string="Sustrato", required=True)
    m2          = fields.Integer(string='Metro Cuadrado', required=True)


