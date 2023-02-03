# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from math import floor

from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError


import logging

_logger = logging.getLogger(__name__)


TIPO_TROQUEL = [
        ('p','PLANO'),
        ('m','MACISO'),
        ('l','LAMINA'),
        ('s','LASER'),
        ('g','MAGNETICO'),
        ]

class TablaTroquel(models.Model):
    _name = 'tabla_troquel'
    _rec_name = 'name'

    producto_id        = fields.Many2one('cotizador.producto', 'Producto', required=True)
    name               = fields.Char(string='Nombre', compute='_compute_name', store=True)
    descripcion        = fields.Char(string='Descripción')

    #------- Campos largo ancho ---------
    # En UoM original
    largo        = fields.Integer(string='Largo', required=True)
    ancho        = fields.Integer(string='Ancho', required=True)
    z            = fields.Integer(string='Z')
    tipo_troquel = fields.Selection(TIPO_TROQUEL,string='tipo_troquel')
    etiquetas_al_ancho      = fields.Integer(string='Etiquetas al Ancho')
    gap                     = fields.Float(string='Gap', compute='_compute_gap', digits=(10, 3))
    gap_minimo              = fields.Float(string='Gap Mímino', default=1.0)
    etiquetas_al_desarrollo = fields.Integer(string='Etiquetas al Desarrollo', compute='_compute_gap')

#    @api.depends('gap')
#    def _compute_et_al_desarrollo(self):
#        for rec in self:
#            if rec.gap > 0:
#                perimetro = round(rec.z * 3.175,3)
#                l = round(perimetro / (rec.largo + rec.gap),0)
#                rec.etiquetas_al_desarrollo = l
#            else:
#                rec.etiquetas_al_desarrollo = 0

    @api.depends('largo', 'ancho')
    def _compute_name(self):
        for rec in self:
            rec.name = "%3s X %3s (Z=%s,S=%s)" % (rec.largo,rec.ancho,rec.z,rec.etiquetas_al_ancho)

#    @api.depends('z', 'largo', 'gap_minimo')
#    def _compute_gap(self):
#        for rec in self:
#            if rec.z > 0 and rec.largo > 0:
#                i = 1
#                c_calc = 0
#                c_calc_ant = 0
#                # Muy importante el redondeo!!!
#                perimetro = round(rec.z * 3.175,3)
#                while True:
#                    c_calc_ant = c_calc
#                    c_calc = perimetro / i  - rec.largo
#
#                    if c_calc < rec.gap_minimo:
#                        break
#                    i = i + 1
#                rec.gap = perimetro / (i-1) - rec.largo
#            else:
#                rec.gap = 0

    @api.depends('z', 'largo', 'gap_minimo')
    def _compute_gap(self):
        for rec in self:
            if rec.z > 0 and rec.largo > 0:
                # Muy importante el redondeo!!!
                perimetro = round(rec.z * 3.175,3)
                c_calc = perimetro / (rec.gap_minimo + rec.largo)
                rec.etiquetas_al_desarrollo = floor(c_calc)
                rec.gap = perimetro / rec.etiquetas_al_desarrollo - rec.largo
            else:
                rec.gap = 0
                rec.etiquetas_al_desarrollo = 0

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.search([('name', operator, name)] + args, limit=limit)
        if not recs.ids:
            return super(TablaTroquel, self).name_search(name=name, args=args,
                                                   operator=operator,
                                                   limit=limit)
        return recs.name_get()
