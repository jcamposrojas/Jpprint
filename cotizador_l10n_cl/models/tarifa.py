# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from math import floor

from odoo import api, fields, models, _, tools
from odoo.exceptions import ValidationError,UserError


import logging

_logger = logging.getLogger(__name__)

# Tarifas

class Tarifa(models.Model):
    _name = 'tarifa'

    producto_id = fields.Many2one('cotizador.producto', string="Sustrato", required=True)
    sustrato_id = fields.Many2one('producto.sustrato', string='Sustrato')
    m2          = fields.Integer(string='Metro Cuadrado')
    porcentaje  = fields.Integer(string='Porcentaje')

#    @api.constrains('producto_id','sustrato_id','m2')
#    def _check_date_end(self):
#        for rec in self:
#            if rec.producto_id and rec.sustrato_id and rec.m2:
#                registro = self.env['tarifa'].search([('producto_id','=',rec.producto_id.id),('sustrato_id','=',rec.sustrato_id.id),('m2','=',rec.m2)])
#                if len(registro) > 1:
#                    raise ValidationError('Ya existe registro')

    _sql_constraints = [
        ('m2_sustrato_uniq', 'unique(producto_id,m2,sustrato_id)', 'Par Metro Cuadrado - Sustrato debe ser único'),
        ('check_porcentaje', 'CHECK(porcentaje > 0)', 'Porcentaje debe ser positivo'),
        ]

    @api.model
    def get_porcentaje(self,sustrato_id,m2):
        registro = self.env['tarifa'].search([('producto_id','=',self.producto_id.id),('sustrato_id','=',sustrato_id.id)])
        _logger.info(' GETPORCENTAJE ')
        for rec in registro:
            _logger.info(rec.m2)


