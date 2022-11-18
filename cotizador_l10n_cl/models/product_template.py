# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _, SUPERUSER_ID

import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    gen_cotizador    = fields.Boolean(string="Creado por Cotizador", default=False)
    lista_parametros = fields.Text(string="Parámetros")

