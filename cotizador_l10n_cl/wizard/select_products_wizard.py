# -*- coding: utf-8 -*-
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import models, fields, api
from math import ceil, floor
import json

import logging

_logger = logging.getLogger(__name__)

class SelectProducts(models.TransientModel):
    _name = 'select.products'
    _description = 'Select Products'

    company_id      = fields.Many2one('res.company', default=lambda self: self.env.company)
    producto_id     = fields.Many2one(comodel_name="cotizador.producto", string="Producto", required=True)
    currency_id     = fields.Many2one('res.currency', readonly=True, related='company_id.currency_id')

    codigo_producto = fields.Char(related='producto_id.codigo')
    sustrato_id     = fields.Many2one(comodel_name="cotizador.sustrato", string="Sustrato", required=True)
    adhesivo_id     = fields.Many2one(comodel_name="cotizador.adhesivo", string="Adhesivo", required=True)
    merma_estimada  = fields.Float(string="Merma sustrato (%)", compute="_compute_merma")

    #========== Datos ==========
    largo         = fields.Integer(string="Largo")
    ancho         = fields.Integer(string="Ancho")
    # Usar estos datos de largo/ancho (usados despues de aplicar aisa)
    largo_interno = fields.Integer(string="Largo AISA", compute='_compute_interno')
    ancho_interno = fields.Integer(string="Ancho AISA", compute='_compute_interno')

    #ancho_papel   = fields.Integer(string="Ancho de papel",compute='_compute_ancho_papel', store=True)
    ancho_papel   = fields.Integer(string="Ancho de papel",default=210)
    cantidad      = fields.Integer(string="Cantidad")
    gap           = fields.Float(string="GAP entre etiquetas", default=3, digits=(10,3))
    engranaje     = fields.Float(string="Paso Engranaje", default=3.175, digits=(10,3))
    etiquetas_al_desarrollo = fields.Integer(string="Etiquetas al desarrollo", default=1)
    # salidas de etiqueta en maquina
    etiquetas_al_ancho      = fields.Integer(string="Etiquetas al ancho", default=2)

    #========== Valores calculados==========
    count_coincidencias = fields.Integer(string="Número de coincidencias")
    z_calculado      = fields.Float(string='Z calculado', compute="_calc_z", digits=(10,3), store=True)
    z_ingreso        = fields.Integer(string='Z ingreso', compute="_calc_z", store=True)
    etiqueta_con_gap = fields.Float(string="Etiqueta con GAP", compute="_calc_z", store=True, digits=(10,3))
    gap_etiqueta     = fields.Float(string="GAP de etiqueta", compute="_calc_z", store=True, digits=(10,3))

    area_ocupada     = fields.Float(string="Superficie ocupada", compute="_calc_z", store=True, digits=(10,3))
    area_ocupada_con_merma  = fields.Float(string="Superficie C/MERMA", compute="_calc_z", store=True, digits=(10,3))
    cilindros        = fields.Integer(string='Cilindros', compute="_calc_z", store=True)
    troquel          = fields.Char(string='Troquel', compute="_calc_z", store=True)
    #---------- Al ancho (falta uom) -------------
    rf    = fields.Integer('RF', default=3)
    sx    = fields.Integer('SX', compute="_calc_z")
    ss    = fields.Integer('SS', compute="_calc_z")
    ancho_bobina = fields.Integer('Ancho Bobina (LX)', compute="_calc_z")
    # Resultado
    longitud_papel = fields.Integer(string="Longitud Papel", compute="_calc_z")

    def _get_default_uom_id(self):
        return self.env.ref('uom.product_uom_millimeter').id

    def _get_default_product_uom_id(self):
        return self.env.ref('uom.product_uom_unit')

    uom_id         = fields.Many2one( 'uom.uom', 'Unidad de medida', default=_get_default_uom_id, required=True)
    product_uom_id = fields.Many2one( 'uom.uom', 'Unidad de medida', default=_get_default_product_uom_id, required=True)

    #buje = fields.Selection( string="Buje", required=True,
    #    selection=[("buje1", "BUJE 1"), ("buje3", "BUJE 3"),("buje40", "BUJE 40")], default="buje1")
    buje_id = fields.Many2one('cotizador.buje', 'Buje')

    rotulado_embalaje = fields.Boolean(string="Rotulado y embalaje", default=True)
    efecto_espejo     = fields.Boolean(string="Efecto Espejo", default=False)
    laminado          = fields.Boolean(string="Laminado", default=True)
    folia             = fields.Boolean(string="Folia", default=True)
    datos_adicionales = fields.Text(string="Comentarios", copy=True)
    codigo            = fields.Char(string="Código Producción", compute="_compute_codigo_nombre", store=True)
    nombre_producto   = fields.Char(string="Nombre producto", compute="_compute_codigo_nombre", store=True)
    texto_adicional   = fields.Char(string="Texto adicional")

    def _default_aisa(self):
        return self.env.ref('cotizador_l10n_cl.aisa_2')

    aisa_id           = fields.Many2one('ir.attachment', string='Etiqueta AISA',
                        domain="[('res_model', '=', 'select.products'), ('res_field', '=', 'aisa_id')]",
                        default=_default_aisa)

    #========== Valores ==========
    insumo_ids    = fields.One2many('cotizador.insumo','select_id', compute='_update_insumos', copy=True, store=True)
    adicional_ids = fields.Many2many(comodel_name='cotizador.adicional', string="Entradas Adicionales")

    precio_total    = fields.Float(string='Precio Total', compute='_compute_price', store=True)
    precio_unitario = fields.Float(string='Precio Unitario', compute='_compute_price', store=True)

    @api.depends('insumo_ids')
    def _compute_price(self):
        for rec in self:
            price = 0.0
            for item in rec.insumo_ids:
                price += item.costo_consumo
            rec.precio_total    = price
            rec.precio_unitario = price / rec.cantidad if rec.cantidad > 0 else 0

    @api.depends('aisa_id', 'largo', 'ancho')
    def _compute_interno(self):
        if 'aisa3' in self.aisa_id.name or 'aisa4' in self.aisa_id.name or \
           'aisa7' in self.aisa_id.name or 'aisa8' in self.aisa_id.name:
            self.largo_interno = self.ancho
            self.ancho_interno = self.largo
        else:
            self.largo_interno = self.largo
            self.ancho_interno = self.ancho

# JCR. no se usa
#    @api.depends('sustrato_id')
#    def _compute_ancho_papel(self):
#        if self.sustrato_id and self.sustrato_id.product_product_id:
#            self.ancho_papel = self.sustrato_id.product_product_id.ancho
#        else:
#            self.ancho_papel = 0


    @api.depends('sustrato_id','producto_id')
    def _compute_merma(self):
        if self.sustrato_id and self.producto_id:
            prod = self.env['producto.sustrato'].search([('sustrato_id','=',self.sustrato_id.id),('producto_id','=',self.producto_id.id)])
            if prod:
                self.merma_estimada = prod.merma
        else:
            self.merma_estimada = 0.0

#    @api.depends('longitud_papel','ancho_bobina')
#    def _calc_area(self):
#        self.area_ocupada = round((self.longitud_papel * self.ancho_bobina) / 1000000, 3)
#        self.area_ocupada_con_merma = round(self.area_ocupada * (1 + (self.merma_estimada / 100.0)), 3)

#    @api.onchange('producto_id')
#    def _get_posible_adicionales(self):
#        if self.producto_id:
#            adicionales = self.producto_id.adicional_ids
            #_logger.info(' ADICIONAL ')
            #_logger.info(adicionales.id)
            #_logger.info(adicionales.name)

        #line = {}
        #for input_adicional in adicionales:
        #    _logger.info(' ADICIONAL ')
        #    _logger.info(input_adicional)
        #    line |= input_adicional
        #self.posible_adicionales = line

        #self.possible_values = attr_values.sorted()


    def asigna_z(self,value):
        valor_propuesto = 0.0
        cilindros       = 0
        name            = ''
        cilindros = self.env['cotizador.troquel'].search([],order='z desc')
        for cil in cilindros:
            if value == cil.z:
                return cil.z, cil.unidades, cil.name
            if value > cil.z:
                #if valor_propuesto == 0.0:
                #    return valor_propuesto, cilindros, name
                    #return cil.z, cil.unidades, cil.name
                return valor_propuesto, cilindros, name
            valor_propuesto = cil.z
            cilindros       = cil.unidades
            name            = cil.name
        return valor_propuesto, cilindros, name

    @api.depends('producto_id', 'sustrato_id', 'largo', 'ancho', 'adhesivo_id', 'texto_adicional')
    def _compute_codigo_nombre(self):
        nombre = ""
        codigo = ""
        if self.producto_id:
            prod_id = self.env['cotizador.producto'].search([('id','=',self.producto_id.id)])
            if prod_id:
                codigo = prod_id.codigo
                nombre = prod_id.nombre_corto
        if self.sustrato_id:
            sust_id = self.env['cotizador.sustrato'].search([('id','=',self.sustrato_id.id)])
            if sust_id:
                codigo = codigo + sust_id.codigo
                nombre += " " + sust_id.nombre_corto

        if self.largo > 0:
            nombre += " " + str(self.largo) + self.uom_id.name

        if self.ancho > 0:
            nombre += "X" + str(self.ancho) + self.uom_id.name

        if self.adhesivo_id:
            nombre += " " + self.adhesivo_id.name

        if self.texto_adicional:
            nombre += " " + self.texto_adicional

        self.nombre_producto = nombre
        self.codigo          = codigo

        # Calcula numero de coincidencias de nombre
        if self.nombre_producto:
            products_count = self.env['product.template'].search_count([('name','ilike',self.nombre_producto)])
            self.count_coincidencias = products_count

    def _set_ancho_efectivo(self, ancho_etiqueta, etiquetas_al_ancho):
        if etiquetas_al_ancho and etiquetas_al_ancho > 0:
            if etiquetas_al_ancho == 1:
                self.ss = 0
                self.sx = 0
            elif etiquetas_al_ancho == 2:
                self.ss = self.producto_id.SS # 6
                self.sx = 0
            elif etiquetas_al_ancho % 2 == 0: # par > 2
                self.ss = self.producto_id.SS # 6
                self.sx = self.producto_id.SX # 3
            elif etiquetas_al_ancho % 2 == 1: # impar
                self.ss = 0
                self.sx = self.producto_id.SS # 6

            self.rf = self.producto_id.RF

            ancho_efectivo = ancho_etiqueta * etiquetas_al_ancho + self.rf * 2
            if etiquetas_al_ancho % 2 == 0:
                ancho_efectivo += (self.ss + 2*((etiquetas_al_ancho / 2 - 1)*(self.sx)))
            else:
                ancho_efectivo += (etiquetas_al_ancho - 1) * self.sx
            return ancho_efectivo
        return 0

    #--------------- Calculo de Z ---------------
    @api.depends('producto_id',
            'sustrato_id',
            'largo_interno',
            'ancho_interno',
            'aisa_id',
            'cantidad',
            'gap',
            'engranaje',
            'etiquetas_al_desarrollo',
            'etiquetas_al_ancho',
            'merma_estimada',
            'rf',
            'etiqueta_con_gap')
    def _calc_z(self):
        self.ss          = 0
        self.sx          = 0
        self.z_calculado = 0
        self.z_ingreso   = 0
        self.etiqueta_con_gap = 0
        self.gap_etiqueta     = 0
        self.area_ocupada            = 0
        self.area_ocupada_con_merma  = 0
        self.cilindros      = 0
        self.troquel        = ''
        self.ancho_bobina   = 0
        self.longitud_papel = 0

        #------------------ Blanca TROQUELADA -------------------
        if self._area_negocio() == '1' or self._area_negocio() == '3':
            self.z_calculado = ((self.largo_interno + self.gap)/self.engranaje) * self.etiquetas_al_desarrollo

            #Ingreso de cilindro
            self.z_ingreso, self.cilindros, self.troquel = self.asigna_z(self.z_calculado)

            self.etiqueta_con_gap = (self.z_ingreso * self.engranaje) / self.etiquetas_al_desarrollo
            self.gap_etiqueta     = self.etiqueta_con_gap - self.largo_interno

            if self.etiquetas_al_ancho:
                if self.etiquetas_al_ancho == 1:
                    self.ss = 0
                    self.sx = 0
                elif self.etiquetas_al_ancho == 2:
                    self.ss = self.producto_id.SS # 6
                    self.sx = 0
                elif self.etiquetas_al_ancho % 2 == 0: # par > 2
                    self.ss = self.producto_id.SS # 6
                    self.sx = self.producto_id.SX # 3
                elif self.etiquetas_al_ancho % 2 == 1: # impar
                    self.ss = 0
                    self.sx = self.producto_id.SS # 6

                self.rf = self.producto_id.RF

                self.ancho_bobina = self.ancho_interno * self.etiquetas_al_ancho + self.rf * 2
                if self.etiquetas_al_ancho % 2 == 0:
                    self.ancho_bobina += (self.ss + 2*((self.etiquetas_al_ancho / 2 - 1)*(self.sx)))
                else:
                    self.ancho_bobina += (self.etiquetas_al_ancho - 1) * self.sx

                _, self.ancho_papel = self.producto_id.get_best_corte(self.sustrato_id, self.ancho_bobina)

                # Longitud
                self.longitud_papel = (self.etiqueta_con_gap * self.cantidad) / self.etiquetas_al_ancho

            # Calcula area
            self.area_ocupada = round((self.longitud_papel * self.ancho_papel) / 1000000, 3)
            self.area_ocupada_con_merma = round(self.area_ocupada * (1 + (self.merma_estimada / 100.0)), 3)
        #--------------------- JETRION ---------------------
        elif self._area_negocio() == '2':
            if self.largo_interno > 0.0 and self.ancho_interno > 0.0 and self.cantidad > 0.0:
                # Toma el primer corte
                _, self.ancho_papel = self.producto_id.get_best_corte(self.sustrato_id, 0)

                #n14 = 210
                n14 = self.ancho_papel
                o14 = round(n14 / self.largo_interno - 0.5,0) # Nro etiquetas (enteras) puestas a lo largo
                p14 = round(n14 / self.ancho_interno - 0.5,0) # Nro etiquetas (enteras) puestas a lo ancho
                f15 = self.ancho_interno if o14 > p14 else self.largo_interno # Avance
                q14 = max(o14,p14) # Etiquetas al ancho

                self.etiquetas_al_ancho = q14
                self.longitud_papel = (self.cantidad * f15) / q14

                f15 = f15 / 1000.0
                self.area_ocupada = round((self.cantidad / q14) * f15 * (self.ancho_papel / 1000.0), 3)
                self.area_ocupada_con_merma = round(self.area_ocupada * (1 + (self.merma_estimada / 100.0)), 3)
            else:
                #self.etiquetas_al_ancho = 0
                self.area_ocupada = 0
                self.area_ocupada_con_merma = 0
        #--------------------- TTR ---------------------
        #--------------------- RESTO ------------------------
        else:
            if self.largo_interno > 0.0 and self.ancho_interno > 0.0 and self.cantidad > 0.0:
                # Entradas:
                #    ancho_interno, self.etiquetas_al_ancho, self.gap

                # En este caso corresponde a ancho calculado, pero se almacena en ancho_bobina
                self.ancho_bobina = self._set_ancho_efectivo(self.ancho_interno, self.etiquetas_al_ancho)
                self.etiqueta_con_gap = self.gap + self.largo_interno

                _, self.ancho_papel = self.producto_id.get_best_corte(self.sustrato_id, self.ancho_bobina)

                # Longitud
                self.longitud_papel = (self.etiqueta_con_gap * self.cantidad) / self.etiquetas_al_ancho

                # Calcula area
                self.area_ocupada = round((self.longitud_papel * self.ancho_papel) / 1000000, 3)
                self.area_ocupada_con_merma = round(self.area_ocupada * (1 + (self.merma_estimada / 100.0)), 3)
            else:
                #self.etiquetas_al_ancho = 0
                self.area_ocupada = 0
                self.area_ocupada_con_merma = 0

        # Largo en metros
#        self.largo_ocupado   = ((self.etiqueta_con_gap * self.cantidad ) / self.etiquetas_al_ancho) / 1000.0
        # Area en metros cuadrados
        #self.area_ocupada    = (self.largo_ocupado * self.ancho_papel)/1000000.0

        # C/MERMA
        # Area en metros cuadrados
        #self.area_ocupada_con_merma   = (self.area_ocupada * (1.0 + self.merma_estimada / 100.0))/1000000.0

    @api.onchange('producto_id')
    def _compute_sustrato_id_domain(self):
        for rec in self:
            rec.sustrato_id = False
            lista = [data.sustrato_id.id for data in self.producto_id.producto_sustrato_ids]
            if lista:
                domain = [('id','in',tuple(lista))]
            else:
                domain = []
            return {'domain': {'sustrato_id':domain}}

    # Actualiza listado de materias primas
    @api.depends('producto_id',
            'sustrato_id',
            'adicional_ids',
            'largo_interno',
            'ancho_interno',
            'cantidad',
            'area_ocupada',
            'merma_estimada',
            'buje_id')
    def _update_insumos(self):
        if self.ancho == 0 or self.largo == 0:
            return

        # Copia items insertados automaticamente para luego recalcularlos
        lst_tmp  = []
        for item in self.insumo_ids:
            if item.flag_adicional == True:
                line_dict = {
                    'name'             : item.name,
                    'cantidad'         : item.cantidad,
                    'uom_id'           : item.uom_id.id,
                    'costo_unitario'   : item.costo_unitario,
                    'costo_consumo'    : item.costo_consumo,
                    'cost_currency_id' : item.cost_currency_id.id,
                    'merma'            : item.merma,
                    'incluido_en_ldm'  : item.incluido_en_ldm,
                    'flag_adicional'   : item.flag_adicional,
                }
                lst_tmp.append(line_dict)
                #self.insumo_ids = [(2,item.id)]
        self.insumo_ids = [(5,0)]

        # Sustrato
        if self.sustrato_id.product_product_id:
            vals = {
                    'select_id': 0,
                    #'select_id': self.id,
                    'product_product_id': self.sustrato_id.product_product_id.id,
                    'cost_currency_id'  : self.sustrato_id.product_product_id.currency_id.id,
                    'name'           : self.sustrato_id.product_product_id.name,
                    'cantidad'       : self.area_ocupada_con_merma,
                    'costo_unitario' : self.sustrato_id.standard_price,
                    'costo_consumo'  : self.sustrato_id.standard_price * self.area_ocupada_con_merma,
                    'uom_id'         : self.sustrato_id.product_product_id.uom_id.id,
                    'merma'          : self.merma_estimada,
                    'incluido_en_ldm': True,
                    'flag_adicional' : False,
                }
            self.insumo_ids = [(0,0,vals)]

        # Consumos obligatorios
        for line in self.producto_id.consumo_ids:
            vals = {
                    'select_id': 0,
                    #'select_id': self.id,
                    'product_product_id': line.product_product_id.id,
                    'cost_currency_id': line.product_product_id.currency_id.id,
                    'name': line.product_product_id.name,
                    'cantidad': line.cantidad * self.area_ocupada * (1 + line.merma / 100.0),
                    'costo_unitario': line.costo_consumo,
                    'costo_consumo': line.costo_consumo * self.area_ocupada * (1 + line.merma / 100.0),
                    'uom_id': line.consumo_uom_id.id,
                    'merma': line.merma,
                    'incluido_en_ldm': line.incluido_en_ldm,
                    'flag_adicional': False,
                }
            self.insumo_ids = [(0,0,vals)]

        #------------------ Productos homologados ---------------------
        largo_total = round((self.longitud_papel / 1000.0), 0) * self.etiquetas_al_ancho
        # Cantidad de productos homologados
        for line in self.producto_id.homologo_ids:
            qty_productos = ceil(largo_total / line.cantidad_homologo)
            vals = {
                'select_id': 0,
                #'select_id': self.id,
                'product_product_id': line.product_product_id.id,
                'cost_currency_id'  : line.cost_currency_id.id,
                'name'              : line.product_product_id.name,
                'cantidad'          : ceil(largo_total / line.cantidad_homologo) , #line.cantidad * self.area_ocupada * (1 + line.merma / 100.0),
                'costo_unitario'    : line.standard_price,
                'costo_consumo'     : line.standard_price * qty_productos, #largo_totallargo_totaline.costo_consumo * self.area_ocupada * (1 + line.merma / 100.0),
                'uom_id'            : line.consumo_uom_id.id,
                'merma'             : line.merma,
                'incluido_en_ldm'   : line.incluido_en_ldm,
                'flag_adicional'    : False,
            }
            self.insumo_ids = [(0,0,vals)]

        #------------------ Cintas TTR ---------------------
        # Solo para TTR
        if self._area_negocio() == '5':
            ttr_id, ttr_ancho = self.producto_id.get_best_ttr(self.ancho_interno)
            _logger.info(' TTR ')
            _logger.info(ttr_ancho)
            if ttr_id:
                # Nro de etiquetas dentro del ancho de cinta
                n_etiquetas_al_ancho = ttr_ancho / self.ancho_interno
                n_cintas_al_ancho = ceil(self.etiquetas_al_ancho / n_etiquetas_al_ancho)
                # Largo total de cinta en mm
                largo_total_cinta = self.longitud_papel * n_cintas_al_ancho

            # Largo total en mm
#            largo_total = self.longitud_papel * self.etiquetas_al_ancho
            #for line in self.producto_id.ttr_ids:
                _logger.info('self.ancho_interno')
                _logger.info(self.ancho_interno)
                _logger.info('n_etiquetas_al_ancho')
                _logger.info(n_etiquetas_al_ancho)
                _logger.info('n_cintas_al_ancho')
                _logger.info(n_cintas_al_ancho)
                _logger.info('largo_total_cinta')
                _logger.info(largo_total_cinta)

                qty_productos = ceil(largo_total_cinta / ttr_id.largo_mm)
                _logger.info('qty_productos')
                _logger.info(qty_productos)
                vals = {
                    'select_id': 0,
                    #'select_id': self.id,
                    'product_product_id': ttr_id.product_product_id.id,
                    'cost_currency_id'  : ttr_id.cost_currency_id.id,
                    'name'              : ttr_id.product_product_id.name,
                    'cantidad'          : qty_productos, #line.cantidad * self.area_ocupada * (1 + line.merma / 100.0),
                    'costo_unitario'    : ttr_id.standard_price,
                    'costo_consumo'     : ttr_id.standard_price * qty_productos, #largo_totallargo_totaline.costo_consumo * self.area_ocupada * (1 + line.merma / 100.0),
                    #'uom_id'            : line.consumo_uom_id.id,
                    'merma'             : ttr_id.merma,
                    'incluido_en_ldm'   : ttr_id.incluido_en_ldm,
                    'flag_adicional'    : False,
                }
                self.insumo_ids = [(0,0,vals)]

        # Buje
        if self.buje_id:
            producto = self.buje_id.product_product_id
            cantidad = round((self.longitud_papel / 1000.0) / self.buje_id.longitud, 0) * self.etiquetas_al_ancho
            vals = {
                    'select_id': 0,
                    'product_product_id': producto.id if producto else None,
                    'cost_currency_id': producto.currency_id.id if producto else None,
                    'name': self.buje_id.name,
                    'cantidad': cantidad,
                    'costo_unitario': self.buje_id.standard_price,
                    'costo_consumo': cantidad * self.buje_id.standard_price,
                    'uom_id': self.buje_id.uom_id.id,
                    'merma': 0,
                    'incluido_en_ldm': True,
                    'flag_adicional': False,
                }
            self.insumo_ids = [(0,0,vals)]


        for line in self.producto_id.adicional_ids:
            if self.producto_id.uom_id.id == line.uom_id.id:
                costo = line.standard_price * line.cantidad * self.area_ocupada
            else:
                costo = line.standard_price * line.cantidad
            vals = {
                    'select_id': 0,
                    #'select_id': self.id,
                    'cost_currency_id': line.cost_currency_id.id,
                    'name': line.name, # Aun por llenar
                    'cantidad': line.cantidad, # Aun por llenar
                    'costo_unitario': line.standard_price,
                    'costo_consumo': costo,
                    'uom_id': line.uom_id.id,
                    #'merma': 0.0, # por definir
                    'incluido_en_ldm': line.incluido_en_ldm,#line.incluido_en_ldm,
                    'flag_adicional': False,
                }
            self.insumo_ids = [(0,0,vals)]

        # Reingresa items creados por el usuario
        for lst in lst_tmp:
            self.insumo_ids = [(0,0,lst)]


    #@api.depends('product_calc_id')
    #def _compute_sustrato_id_domain(self):
    #    for rec in self:
    #        rec.sustrato_id = False
    #        lista = [data.id for data in self.product_calc_id.sustratos_ids]
    #        if lista:
    #            #rec.sustrato_id_domain = json.dumps([('id','in',lista)]) 
    #            rec.sustrato_id_domain = [('id','in',tuple(lista))]
    #        else:
    #            rec.sustrato_id_domain = []

#    product_ids = fields.Many2many('product.product', string='Products')
#    flag_order  = fields.Char('Flag Order')

    def add_product(self):
        product = self.create_product()
        if product:
            product.product_tmpl_id.gen_cotizador = True

            ############### FABRICACION ###################
            #------- Rutas de producto (MTO y Fabricar) --------
            stock_id = self.env.ref('stock.route_warehouse0_mto').id
            mrp_id   = self.env.ref('mrp.route_warehouse0_manufacture').id
            product.route_ids = [(5,0)] + [(4,stock_id),(4,mrp_id)]

            #---------------- Crear BoM ------------------------
            vals = {
                    'product_tmpl_id'     : product.product_tmpl_id.id,
                    'type'                : 'normal', # Fabricar este producto
                    'product_qty'         : self.cantidad,
                    'analytic_account_id' : self.producto_id.analytic_account_id.id or None, # Actualiza cta analitica en SO line
                }
            mrp = self.env["mrp.bom"].create(vals)

            list_parametros = {'content':[]}
            count_parametros = 0
            self._update_insumos() # Se vuelve a llamar. Los valores llegaban en 0.
            for line in self.insumo_ids:
                # BOM lines
                if line.incluido_en_ldm:
                    vals = {
                        'bom_id':         mrp.id,
                        'product_id':     line.product_product_id.id,
                        'product_qty':    line.cantidad,
                        'product_uom_id': line.uom_id.id,
                    }
                    #'uom_id': self.sustrato_id.product_product_id.uom_id.id,
                    mrp.bom_line_ids = [(0,0,vals)]

                # Parametros
                if line.product_product_id:
                    name = line.product_product_id.name
                else:
                    name = line.name
                val = {
                    'producto'  : name or '',
                    #'moneda'    : line.cost_currency_id.symbol if line.flag_adicional else line.product_product_id.currency_id.symbol,
                    'moneda'    : line.cost_currency_id.symbol if not line.incluido_en_ldm else line.product_product_id.currency_id.symbol,
                    'uom'       : line.uom_id.name or '',
                    'cantidad'  : line.cantidad or '',
                    'monto'     : round(line.costo_consumo) or '',
                    'merma'     : line.merma or '',
                    'incluido_en_ldm': line.incluido_en_ldm or '',
                    'flag_adicional' : line.flag_adicional or '',
                }
                list_parametros['content'].append(val)
                count_parametros += 1

            list_parametros['count_parametros'] = count_parametros
            list_parametros['data'] = {}
            list_parametros['data']['largo'] = self.largo
            list_parametros['data']['ancho'] = self.ancho
            list_parametros['data']['texto_adicional']   = self.texto_adicional or ''
            list_parametros['data']['datos_adicionales'] = self.datos_adicionales or ''
            list_parametros['data']['longitud_papel']    = self.longitud_papel
            list_parametros['data']['area_ocupada']      = self.area_ocupada
            list_parametros['data']['area_ocupada_con_merma'] = self.area_ocupada_con_merma
            if self.aisa_id:
                list_parametros['data']['aisa'] = self.aisa_id.name.replace('.png','').upper()
            else:
                list_parametros['data']['aisa'] = ''

            #-------------- Parametros relacionados al area de negocio ----------------
            list_parametros['param'] = {}
            list_parametros['param']['area_negocio'] = self._area_negocio()
            if self._area_negocio() == '1' or self._area_negocio() == '3':
                list_parametros['param']['engranaje'] = self.engranaje
                list_parametros['param']['z_calculado'] = self.z_calculado
                list_parametros['param']['z_ingreso']   = self.z_ingreso
                list_parametros['param']['cilindros']   = self.cilindros
                list_parametros['param']['troquel']     = self.troquel
                list_parametros['param']['gap_etiqueta']     = self.gap_etiqueta
                list_parametros['param']['etiqueta_con_gap'] = self.etiqueta_con_gap
                list_parametros['param']['rf'] = self.rf
                list_parametros['param']['ss'] = self.ss
                list_parametros['param']['sx'] = self.sx
                list_parametros['param']['etiquetas_al_ancho'] = self.etiquetas_al_ancho
                list_parametros['param']['etiquetas_al_desarrollo'] = self.etiquetas_al_desarrollo
                list_parametros['param']['ancho_bobina']       = self.ancho_bobina
                list_parametros['param']['ancho_papel']        = self.ancho_papel
            elif self._area_negocio() == '2':
                list_parametros['param']['etiquetas_al_ancho'] = self.etiquetas_al_ancho
                list_parametros['param']['ancho_papel']        = self.ancho_papel


            product.lista_parametros = json.dumps(list_parametros)

#            if self.sustrato_id.product_product_id:
#                vals = {
#                    'bom_id': mrp.id,
#                    'product_id': self.sustrato_id.product_product_id.id,
#                    'product_qty': 0,
#                }
#                mrp.bom_line_ids = [(0,0,vals)]
#            for adicional in self.posible_adicionales:
#                values = {
#                    'bom_id': mrp.id,
#                    'product_id': adicional.product_product_id.id,
#                    'product_qty': 0,
#                }
#                mrp.bom_line_ids = [(0,0,values)]


            values = {
                #"product_id": 21, #ID
                #"product_id": self.sustrato_id.product_id.id, #ID
                "product_tmpl_id": product.product_tmpl_id.id, #ID
                "product_qty": self.cantidad, #Cantidad a producir=Cantidad en BOM
                #"bom_id": mrp.id
            }
            # Comentado por ahora
            #mrp.bom_line_ids = [(0,0,values)]

            #values = {
            #    'name': 'PRE PRENSA',
            #    'workcenter_id': 1, #ID
            #    'bom_id': mrp.id, #ID
            #}

            for operation in self.producto_id.operation_ids:
                values = {
                    'name': operation.name,
                    'workcenter_id': operation.workcenter_id.id, #ID
                    'bom_id': mrp.id, #ID
                    #Agregar resto de campos de mrp.routing.workcenter.tmp
                    'worksheet_type': 'text',
                    'note': product.lista_parametros,
                }
                mrp.operation_ids = [(0,0,values)]


            # Calcula costo en base a LdM
            # Revisar si es necesario
            #product.button_bom_cost()

            #----------- Insertar producto en SO ------------------
            order_id = self.env['sale.order'].browse(self._context.get('active_id', False))
            if order_id:
                order_line_id = self.env['sale.order.line'].create({
                    'product_id'          : product.id,
                    'product_uom'         : product.uom_id.id,
                    'product_uom_qty'     : self.cantidad,
                    #'price_unit': product.list_price,
                    'analytic_account_id' : self.producto_id.analytic_account_id.id or None, # Actualiza cta analitica en SO line
                    'order_id'            : order_id.id,
                })
            #------------ Agrega TAG Analitico -----------------
            if order_line_id:
                order_line_id.analytic_tag_ids = [(0,0,{'name':order_id.name})]

            # JCR. No usado por ahora
            #product.description = self.genera_descripcion()


    def create_product(self):
        if self.nombre_producto:
#            standard_price = 0.0
#            for item in self.insumo_ids:
#                standard_price += item.costo_consumo
#            standard_price = standard_price / self.cantidad
#            list_price = standard_price # precio/costo unitario

            seq = self.env['ir.sequence'].next_by_code('cotizador_l10n_cl.product')
            vals = {
                "type"           : "product",
                "name"           : self.nombre_producto,
                "default_code"   : self.codigo + '-' + str(seq),
                "purchase_ok"    : False,  # Producto no se compra
                #"description": self.datos_adicionales,
                "categ_id"       : self.producto_id.category_id.id,
                "standard_price" : self.precio_unitario,
                "list_price"     : self.precio_unitario,
                "uom_id"         : self.product_uom_id.id,
            }
            product = self.env["product.product"].create(vals)
            return product
        else:
            return False

    def genera_descripcion(self):
        texto = ""
        if self.buje_id:
            texto =  "BUJE: " + self.buje_id.name +"<br>"
        if self.aisa_id:
            texto += "AISA: " + self.aisa_id.name +"<br>"
        if self.adhesivo_id:
            texto += "ADHESIVO: " + self.adhesivo_id.name +"<br>"
        if self.datos_adicionales:
            texto += "DATOS ADICIONALES:<br>" + self.datos_adicionales +"<br>"

        return texto


    def _area_negocio(self):
        if not self.producto_id:
            return ''

        if self.producto_id.id == self.env.ref('cotizador_l10n_cl.producto1').id:
            return '1'
        elif self.producto_id.id == self.env.ref('cotizador_l10n_cl.producto2').id:
            return '2'
        elif self.producto_id.id == self.env.ref('cotizador_l10n_cl.producto3').id:
            return '3'
        elif self.producto_id.id == self.env.ref('cotizador_l10n_cl.producto4').id:
            return '4'
        elif self.producto_id.id == self.env.ref('cotizador_l10n_cl.producto5').id:
            return '5'
        elif self.producto_id.id == self.env.ref('cotizador_l10n_cl.producto6').id:
            return '6'
        elif self.producto_id.id == self.env.ref('cotizador_l10n_cl.producto7').id:
            return '7'
        elif self.producto_id.id == self.env.ref('cotizador_l10n_cl.producto8').id:
            return '8'

