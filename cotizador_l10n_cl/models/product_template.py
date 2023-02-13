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
    producto_id  = fields.Many2one('cotizador.producto', string="Producto")
    sustrato_id  = fields.Many2one('cotizador.sustrato', string="Sustrato")
    area_ocupada_con_merma  = fields.Float(string="Superficie C/MERMA")

    #tarifa
    def price_compute(self, price_type, uom=False, currency=False, company=False):
        """Return dummy not falsy prices when computation is done from supplier
        info for avoiding error on super method. We will later fill these with
        correct values.
        """
        if price_type == "cotizador":
            return dict.fromkeys(self.ids, 1.0)
        return super().price_compute(
            price_type, uom=uom, currency=currency, company=company
        )

    def _get_tarifa_pricelist_price(self):
        # Solo si el producto fue creado producto de una cotización
        if self.gen_cotizador:
            registro = self.env['tarifa'].search([('producto_id','=',self.producto_id.id),('sustrato_id','=',self.sustrato_id.id)], order='m2 asc')
            #mx = max(registro.mapped('m2'))
            #mn = min(registro.mapped('m2'))
            superficie = self.area_ocupada_con_merma
            #_logger.info("min -> %s, max -> %s"%(mn,mx))
            j = 0
            last = None
            for rec in registro:
                #_logger.info(rec.m2)
                if superficie <= rec.m2:
                    return self._calcula_precio(rec.porcentaje)
                last = rec
                j = j + 1
            return self._calcula_precio(last.porcentaje)

    def _calcula_precio(self,margen):
        return self.standard_price / (1 - margen / 100.0)

