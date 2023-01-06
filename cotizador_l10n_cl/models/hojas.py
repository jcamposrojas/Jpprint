from odoo import api, fields, models, tools, _
from math import floor

import logging

_logger = logging.getLogger(__name__)


class CotizadorHojas(models.Model):
    _name = 'producto_hojas'
    _description = 'Hojas de Papel'

    name        = fields.Char(string='Nombre', required=True)
#    producto_id = fields.Many2one('cotizador.producto', 'Producto', required=True)

    ancho = fields.Integer(string='Ancho de Hoja', required=True)
    alto  = fields.Integer(string='Alto de Hoja', required=True)

    def _get_default_uom_id(self):
        return self.env.ref('uom.product_uom_millimeter')

    uom_id = fields.Many2one('uom.uom', string='Unidad de Medida', default=_get_default_uom_id)
 
#    codigo  = fields.Char(string='Descripción', compute='_compute_name', store=True)
    _sql_constraints = [
        ('ancho_alto_hoja_uniq', 'unique (ancho,alto)', 'El tamaño de hoja debe ser único.'),
        ]

    #
    def get_max(self,largo,ancho,gap,sx,rf):
        #--------------- Optimiza rotando la etiqueta -----------
        # Todos en mm, mm2
        tot_area_out   = self.alto * self.ancho
        # Sin rotar
        et_alto_1, n_al_alto_1, et_ancho_1, n_al_ancho_1 = self._max_etiquetas_xy(largo,self.alto,ancho,self.ancho,gap,sx,rf)
        tot_area_in    = et_alto_1 * et_ancho_1
        diff1          = tot_area_out - tot_area_in
        # Rotado
        et_alto_2, n_al_alto_2, et_ancho_2, n_al_ancho_2 = self._max_etiquetas_xy(ancho,self.alto,largo,self.ancho,gap,sx,rf)
        tot_area_in    = et_alto_2 * et_ancho_2
        diff2          = tot_area_out - tot_area_in
        #_logger.info("COMPARATIVO")
        #_logger.info("%s %s %s/ %s %s %s"%(largo, et_alto_1, n_al_alto_1, ancho, et_ancho_1, n_al_ancho_1))
        #_logger.info("%s %s %s/ %s %s %s"%(ancho, et_alto_2, n_al_alto_2, largo, et_ancho_2, n_al_ancho_2))
        if diff1 <= diff2:
            return False, et_alto_1, n_al_alto_1, et_ancho_1, n_al_ancho_1
            #return largo, et_alto_1, n_al_alto_1, ancho, et_ancho_1, n_al_ancho_1
        else:
            return True, et_alto_2, n_al_alto_2, et_ancho_2, n_al_ancho_2
            #return ancho, et_alto_2, n_al_alto_2, largo, et_ancho_2, n_al_ancho_2

    def _max_etiquetas_xy(self,alto,alto_tot,ancho,ancho_tot,gap,sx,rf):
        i = 1
        c_calc = 0
        c_ancho_ant = 0
        while True:
            c_ancho_ant = c_calc

            c_calc = sx * (i - 1) + i * ancho + 2 * rf

            if c_calc > ancho_tot:
                break
            i = i + 1
        n_ancho = i - 1

        i = 1
        c_calc = 0
        c_alto_ant = 0
        while True:
            c_alto_ant = c_calc

            c_calc = gap * (i - 1) + i * alto + 2 * rf

            if c_calc > alto_tot:
                break
            i = i + 1
        n_alto = i - 1

        return c_alto_ant, n_alto, c_ancho_ant, n_ancho

