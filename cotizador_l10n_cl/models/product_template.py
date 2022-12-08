# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _, SUPERUSER_ID

import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    gen_cotizador    = fields.Boolean(string="Creado por Cotizador", default=False)
    lista_parametros = fields.Text(string="Parámetros")

    def _get_default_largo_ancho_category_uom_id(self):
        return self.env.ref('uom.uom_categ_length').id

    def _get_default_largo_ancho_uom_id(self):
        return self.env.ref('uom.product_uom_millimeter').id

    largo            = fields.Integer(string="Largo")
    ancho            = fields.Integer(string="Ancho")

    largo_ancho_category_uom_id = fields.Many2one('uom.uom', string='Categoría Unidad de Medida Largo Ancho',
                         default=_get_default_largo_ancho_category_uom_id)

    largo_uom_id = fields.Many2one('uom.uom', string='Unidad de Medida Largo',
                         default=_get_default_largo_ancho_uom_id)
    ancho_uom_id = fields.Many2one('uom.uom', string='Unidad de Medida Ancho',
                         default=_get_default_largo_ancho_uom_id)

