# -*- coding: utf-8 -*-
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import models, fields, api
from math import ceil, floor
from odoo.exceptions import UserError, ValidationError
import json

import logging

_logger = logging.getLogger(__name__)


class SelectProducts(models.TransientModel):
    _name = 'select.products'
    _description = 'Select Products'

    SELECT_LARGO = []

    company_id      = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id     = fields.Many2one('res.currency', related='company_id.currency_id')
    currency_symbol = fields.Char(string='Símbolo moneda', related='company_id.name')

    use_aisa            = fields.Boolean('Usa AISA', related='producto_id.use_aisa')
    use_bujes           = fields.Boolean('Usa bujes', related='producto_id.use_bujes')
    use_tinta_blanca    = fields.Boolean('Usa Cobertura Tinta Blanca', related='producto_id.use_tinta_blanca')
    use_cobertura_tinta = fields.Boolean('Cobertura Tinta Blanca', default=False)
    cobertura_tinta     = fields.Many2one(comodel_name='tinta_blanca_lines')
    use_tabla_troquel   = fields.Boolean(string='Usa Tabla Troqueles', related='producto_id.use_tabla_troquel')
    use_cinta_ttr       = fields.Boolean(string='Usa Cinta TTR', related='producto_id.use_cinta_ttr')
    use_cuatricomia     = fields.Boolean(string='Usa Colores', related='producto_id.use_cuatricomia')
    use_cortes          = fields.Boolean(string='Usa Cortes de papel', related='producto_id.use_cortes')
    use_adhesivo        = fields.Boolean(string='Usa Adhesivo', related='producto_id.use_adhesivo')

    producto_id     = fields.Many2one(comodel_name="cotizador.producto", string="Producto", required=True)
    sustrato_id     = fields.Many2one(comodel_name="cotizador.sustrato", string="Sustrato", required=True)
    codigo_producto = fields.Char(related='producto_id.codigo')
    adhesivo_id     = fields.Many2one(comodel_name="cotizador.adhesivo", string="Adhesivo")
    adhesivo_str    = fields.Char(string="Adhesivo Str", default="NA")
    merma_estimada  = fields.Float(string="Merma sustrato (%)", compute="_compute_merma")


    select_largo    = fields.Many2one(comodel_name='tabla_troquel', string="Avance X Ancho", domain="[('producto_id','=',producto_id.id)]")

    #========== Datos ==========
    largo         = fields.Integer(string="Avance")
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
    #-------- Longitud de papel -------------
    longitud_papel = fields.Integer(string="Longitud Papel", compute="_calc_z")
    # Supone que ancho no varia
    longitud_papel_con_merma = fields.Integer(string="Longitud Papel C/MERMA", compute="_calc_z")

    def _get_default_uom_id(self):
        return self.env.ref('uom.product_uom_millimeter').id

    def _get_default_product_uom_id(self):
        return self.env.ref('uom.product_uom_unit').id

    uom_id         = fields.Many2one( 'uom.uom', 'UdM', default=_get_default_uom_id, required=True)
    product_uom_id = fields.Many2one( 'uom.uom', 'Unidad de medida',
                     default=_get_default_product_uom_id, required=True)

    # Dato de cliente. Numero de etiquetas al ancho solicitada por cliente
    salidas_x_rollo = fields.Integer(string='Salidas por rollo')

    #----------- Bujes ------------------
    buje_id           = fields.Many2one('cotizador.buje', 'Buje')
    etiquetas_x_rollo = fields.Integer(string='Etiquetas por rollo', default=0)

    rotulado_embalaje = fields.Boolean(string="Rotulado y embalaje", default=True)
    efecto_espejo     = fields.Boolean(string="Efecto Espejo", default=False)
    laminado          = fields.Boolean(string="Laminado", default=True)
    folia             = fields.Boolean(string="Folia", default=True)
    datos_adicionales = fields.Text(string="Comentarios", copy=True)
    codigo            = fields.Char(string="Código Producción", compute="_compute_codigo_nombre", store=True)
    nombre_producto   = fields.Char(string="Nombre producto", compute="_compute_codigo_nombre", store=True)
    texto_adicional   = fields.Char(string="Texto adicional")

    #----------- AISA -------------
    indica_aisa       = fields.Boolean('Indica AISA?', default=False)
    # No es obligatorio. Solo en caso que el cliente lo solicite
    aisa_id           = fields.Many2one('ir.attachment', string='Etiqueta AISA',
                        domain="[('res_model', '=', 'select.products'), ('res_field', '=', 'aisa_id')]")

    #========== Valores ==========
    #insumo_ids    = fields.One2many('cotizador.insumo','select_id', compute='_update_insumos', copy=True)
    insumo_ids    = fields.One2many('cotizador.insumo', 'select_id', copy=True)
    #adicional_ids = fields.Many2many('cotizador.adicional', 'producto_id', string="Entradas Adicionales")
    adicional_ids = fields.Many2many('cotizador.adicional', string="Entradas Adicionales")
    domain_adicional_ids = fields.Many2many('cotizador.adicional', compute="_compute_domain_adicionales_ids")
    count_adicional_ids  = fields.Integer(string="Count adicionales", compute="_compute_domain_adicionales_ids")

    lista_adicionales_ids = fields.One2many('lista.adicionales', 'select_id')
    domain_lista_adicionales_ids     = fields.Many2many('cotizador.adicional', compute="_compute_domain_adicionales_ids")
    count_lista_adicionales_ids      = fields.Integer(string="Count lista adicionales", compute="_compute_domain_adicionales_ids")

    precio_total    = fields.Float(string='Precio Total', compute='_compute_price', store=True)
    precio_unitario = fields.Float(string='Precio Unitario', compute='_compute_price', store=True)

    domain_hoja_ids        = fields.Many2many('producto_hojas', compute="_compute_domain_adicionales_ids")


    #---------------- Cuatricomia (Flexo) -------------------
    use_barniz  = fields.Boolean('Usa Barniz', default=True)
    use_cyan    = fields.Boolean('Usa Cyan', default=True)
    use_black   = fields.Boolean('Usa Black', default=True)
    use_yellow  = fields.Boolean('Usa Yellow', default=True)
    use_magenta = fields.Boolean('Usa Magenta', default=True)
    use_color1  = fields.Boolean('Color1', default=False)
    use_color2  = fields.Boolean('Color2', default=False)
    use_color3  = fields.Boolean('Color3', default=False)
    use_color4  = fields.Boolean('Color4', default=False)
    color1      = fields.Char('Color1')
    color2      = fields.Char('Color2')
    color3      = fields.Char('Color3')
    color4      = fields.Char('Color4')

    #---------------- RICHO --------------------
    hoja_id           = fields.Many2one('producto_hojas', string='Tamaño Hoja')
    etiquetas_x_hoja  = fields.Integer(string="Etiquetas por hoja", default=0)
    n_hojas           = fields.Integer(string="Número de hojas", default=0)
    n_hojas_con_merma = fields.Integer(string="Número de hojas C/MERMA", default=0)
    alto_papel        = fields.Integer(string="Alto papel")
    rota_etiqueta     = fields.Boolean('Rota etiqueta', default=False)

    @api.depends('producto_id')
    def _compute_domain_adicionales_ids(self):
        for rec in self:
            if rec.producto_id:
                l           = []
                lsolo       = []
                count_l     = 0
                count_lsolo = 0
                for lin in rec.producto_id.adicional_ids:
                    if lin.obligatorio == False:
                        if lin.add_data == False:
                            lsolo.append(lin.id)
                            count_lsolo = count_lsolo + 1
                        else:
                            l.append(lin.id)
                            count_l = count_l + 1
                rec.domain_lista_adicionales_ids = l
                rec.domain_adicional_ids         = lsolo
                rec.count_lista_adicionales_ids  = count_l
                rec.count_adicional_ids          = count_lsolo
            else:
                rec.domain_lista_adicionales_ids = []
                rec.domain_adicional_ids         = []
                rec.count_lista_adicionales_ids  = 0
                rec.count_adicional_ids          = 0

            if rec.use_cortes == False:
                rec.domain_hoja_ids = rec.producto_id.hoja_ids
            else:
                rec.domain_hoja_ids = []

    @api.constrains('salidas_x_rollo')
    def _check_salidas(self):
        for rec in self:
            if rec.use_bujes and rec.salidas_x_rollo <= 0:
                raise ValidationError('Salidas por rollo debe ser > 0')

    @api.depends('insumo_ids')
    def _compute_price(self):
        for rec in self:
            price = 0.0
            for item in rec.insumo_ids:
                price += item.costo_consumo
            rec.precio_total    = price
            rec.precio_unitario = price / rec.cantidad if rec.cantidad > 0 else 0

    @api.depends('largo', 'ancho')
    def _compute_interno(self):
        for rec in self:
            # Largo/ancho en mm
            rec.largo_interno = rec.uom_id._compute_quantity(rec.largo,self.env.ref('uom.product_uom_millimeter'))
            rec.ancho_interno = rec.uom_id._compute_quantity(rec.ancho,self.env.ref('uom.product_uom_millimeter'))

    @api.depends('sustrato_id','producto_id')
    def _compute_merma(self):
        if self.sustrato_id and self.producto_id:
            prod = self.env['producto.sustrato'].search([('sustrato_id','=',self.sustrato_id.id),('producto_id','=',self.producto_id.id)])
            if prod:
                self.merma_estimada = prod.merma
        else:
            self.merma_estimada = 0.0


    def asigna_z(self,value):
        valor_propuesto = 0.0
        cilindros       = 0
        name            = ''
        cilindros = self.env['cotizador.troquel'].search([],order='z desc')
        for cil in cilindros:
            if value == cil.z:
                return cil.z, cil.unidades, cil.name
            if value > cil.z:
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

        if self.use_adhesivo == True and self.adhesivo_id:
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

    @api.onchange('select_largo')
    def _onchange_select_largo(self):
        self.largo = self.select_largo.largo
        self.ancho = self.select_largo.ancho

    #--------------- Calculo de Z ---------------
    @api.depends('producto_id',
            'sustrato_id',
            'largo_interno',
            'ancho_interno',
            'aisa_id',
            'cantidad',
            'gap',
#            'engranaje',
            'etiquetas_al_desarrollo',
            'etiquetas_al_ancho',
            'merma_estimada',
            'rf',
            'etiqueta_con_gap',
            'hoja_id')
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
        self.longitud_papel_con_merma = 0

        #------------------ Blanca TROQUELADA -------------------
        if self._area_negocio() == '1' or self._area_negocio() == '3':
            if self.use_tabla_troquel:
                if self.select_largo:
                    self.largo        = self.select_largo.largo
                    self.ancho        = self.select_largo.ancho
                    self.z_ingreso    = self.select_largo.z
                    self.gap_etiqueta = self.select_largo.gap
                    self.etiqueta_con_gap   = self.select_largo.gap + self.largo_interno
                    self.etiquetas_al_ancho = self.select_largo.etiquetas_al_ancho
                    self.etiquetas_al_desarrollo = round(self.z_ingreso * self.engranaje,3) / self.etiqueta_con_gap
            else:
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
                self.longitud_papel_con_merma = round(self.longitud_papel * (1 + (self.merma_estimada / 100.0)), 3)

            # Calcula area
            self.area_ocupada = round((self.longitud_papel * self.ancho_papel) / 1000000, 3)
            self.area_ocupada_con_merma = round(self.area_ocupada * (1 + (self.merma_estimada / 100.0)), 3)

        #--------------------- JETRION ---------------------
        elif self._area_negocio() == '2':
            if self.largo_interno > 0.0 and self.ancho_interno > 0.0 and self.cantidad > 0.0:
                # Toma el primer corte
                _, self.ancho_papel = self.producto_id.get_best_corte(self.sustrato_id, 0)


                self.gap_etiqueta     = self.producto_id.default_gap
                #--------------- Optimiza rotando la etiqueta -----------
                max_et_1, a    = self._max_etiquetas_al_ancho(self.ancho_interno,self.ancho_papel)
                n_col          = ceil(self.cantidad / max_et_1)
                tot_largo_1    = (self.largo_interno + self.gap_etiqueta) * n_col
                tot_area_in    = tot_largo_1 * a
                tot_area_out_1 = tot_largo_1 * self.ancho_papel
                diff1          = tot_area_out_1 - tot_area_in

                max_et_2, a    = self._max_etiquetas_al_ancho(self.largo_interno,self.ancho_papel)
                n_col          = ceil(self.cantidad / max_et_2)
                tot_largo_2    = (self.ancho_interno + self.gap_etiqueta) * n_col
                tot_area_in    = tot_largo_2 * a
                tot_area_out_2 = tot_largo_2 * self.ancho_papel
                diff2          = tot_area_out_2 - tot_area_in


                if diff1 < diff2:
                    self.etiquetas_al_ancho = max_et_1
                    self.longitud_papel     = tot_largo_1
                    self.area_ocupada       = tot_area_out_1 / 1000000.0
                else:
                    self.etiquetas_al_ancho = max_et_2
                    self.longitud_papel     = tot_largo_2
                    self.area_ocupada       = tot_area_out_2 / 1000000.0

                self.longitud_papel_con_merma = round(self.longitud_papel * (1 + (self.merma_estimada / 100.0)), 3)

                self.area_ocupada_con_merma = round(self.area_ocupada * (1 + (self.merma_estimada / 100.0)), 3)
            else:
                #self.etiquetas_al_ancho = 0
                self.area_ocupada             = 0
                self.area_ocupada_con_merma   = 0
                self.longitud_papel           = 0
                self.longitud_papel_con_merma = 0
        #--------------------- RICHO ---------------------
        elif self._area_negocio() == '7' or self._area_negocio() == '8':
            if self.hoja_id and self.largo_interno > 0.0 and self.ancho_interno > 0.0 and self.cantidad > 0.0:
                #a, b, na, nb = self.hoja_id.get_max(self.largo_interno,self.ancho_interno,self.producto_id.default_gap,self.producto_id.SX,self.producto_id.RF)
                self.ancho_papel = self.hoja_id.ancho
                self.alto_papel  = self.hoja_id.alto
                self.sx          = self.producto_id.SX
                self.rf          = self.producto_id.RF
                self.gap         = self.producto_id.default_gap

                self.rota_etiqueta, et_alto, self.etiquetas_al_desarrollo, et_ancho, self.etiquetas_al_ancho = \
                        self.hoja_id.get_max(self.largo_interno,self.ancho_interno, \
                        self.gap,self.sx,self.rf)
                #_logger.info("%s -> %s %s - %s %s" % (rota, et_alto, self.etiquetas_al_desarrollo, et_ancho, self.etiquetas_al_ancho))
                self.etiquetas_x_hoja  = self.etiquetas_al_desarrollo * self.etiquetas_al_ancho
                self.n_hojas           = ceil(self.cantidad / self.etiquetas_x_hoja)
                #self.n_hojas_con_merma
                area_x_hoja             = self.hoja_id.ancho * self.hoja_id.alto / 1000000
                self.area_ocupada             = area_x_hoja * self.n_hojas # en m2
                #self.area_ocupada_con_merma   = 0
                if self.merma_estimada > 0:
                    self.n_hojas_con_merma = ceil((self.area_ocupada * (1 + (self.merma_estimada / 100.0))) / area_x_hoja)
                else:
                    self.n_hojas_con_merma = self.n_hojas
                self.area_ocupada_con_merma = self.n_hojas_con_merma * area_x_hoja

            #self.etiqueta_con_gap = self.gap + self.largo_interno

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
                self.longitud_papel_con_merma = round(self.longitud_papel * (1 + (self.merma_estimada / 100.0)), 3)

                # Calcula area
                self.area_ocupada = round((self.longitud_papel * self.ancho_papel) / 1000000, 3)
                self.area_ocupada_con_merma = round(self.area_ocupada * (1 + (self.merma_estimada / 100.0)), 3)
            else:
                #self.etiquetas_al_ancho = 0
                self.area_ocupada             = 0
                self.area_ocupada_con_merma   = 0
                self.longitud_papel           = 0
                self.longitud_papel_con_merma = 0

    # Usado por Jetrion
    def _max_etiquetas_al_ancho(self,ancho,total):
        i = 1
        c_ancho = 0
        while True:
            c_ancho_ant = c_ancho

            if i % 2 == 0: # par
                c_ancho = self.producto_id.SS + self.producto_id.SX * (i - 2)
            else: # impar 
                c_ancho = self.producto_id.SX * (i - 1)

            c_ancho = c_ancho + i * ancho + 2 * self.producto_id.RF

            if c_ancho > total:
                break
            i = i + 1

        return i - 1, c_ancho_ant


    @api.onchange('producto_id')
    def _compute_sustrato_id_domain(self):
        for rec in self:
            rec.sustrato_id = False
            # Adicionales
            #rec.adicional_ids         = [(5,0)]
            #rec.lista_adicionales_ids = [(5,0)]

            lista = [data.sustrato_id.id for data in self.producto_id.producto_sustrato_ids]
            if lista:
                domain = [('id','in',tuple(lista))]
            else:
                domain = []
            return {'domain': {'sustrato_id':domain }}


    def _prepare_vals_generico(self, adicional):
        nombre = adicional.name

        #---- cantidad y costo ---
        cantidad = 0
        costo    = 0
        if adicional.tipo_calculo == 'f':
            cantidad = adicional.cantidad
            costo    = adicional.costo_unitario_consumo
        elif adicional.tipo_calculo == 'm2':
            cantidad = adicional.cantidad * self.area_ocupada
            costo = cantidad * adicional.costo_unitario_consumo
        elif adicional.tipo_calculo == 'm':
            cantidad = adicional.cantidad * self.longitud_papel
            costo = cantidad * adicional.costo_unitario_consumo
        elif adicional.tipo_calculo == 'm2+m':
            cantidad = adicional.cantidad * self.area_ocupada_con_merma
            costo = cantidad * adicional.costo_unitario_consumo
        elif adicional.tipo_calculo == 'm+m':
            cantidad = adicional.cantidad * self.longitud_papel_con_merma
            costo = cantidad * adicional.costo_unitario_consumo
        elif adicional.tipo_calculo == 'h':
            cantidad = adicional.cantidad * self.n_hojas
            costo = cantidad * adicional.costo_unitario_consumo
        elif adicional.tipo_calculo == 'hm':
            cantidad = adicional.cantidad * self.n_hojas_con_merma
            costo = cantidad * adicional.costo_unitario_consumo

        if adicional.product_product_id:
            product_id = adicional.product_product_id.id
        else:
            product_id = None

        vals = {
            #'producto_id': 0,
            'cost_currency_id'  : adicional.cost_currency_id.id,
            'name'              : nombre,
            'product_product_id': product_id,
            'cantidad'          : cantidad * (1 + adicional.merma / 100.0),
            'costo_unitario'    : adicional.costo_unitario_consumo,
            'costo_consumo'     : costo * (1 + adicional.merma / 100.0),
            'uom_id'            : adicional.uom_id_de_consumo.id,
            'merma'             : adicional.merma,
            'incluido_en_ldm'   : adicional.incluido_en_ldm,
            'flag_adicional'    : False,
        }
        return vals


    # Actualiza listado de materias primas
    @api.onchange('producto_id',
            'sustrato_id',
            'adicional_ids',
            'lista_adicionales_ids',
            'largo_interno',
            'ancho_interno',
            'cantidad',
            'area_ocupada',
            'merma_estimada',
            'buje_id',
            'salidas_x_rollo',
            'use_tinta_blanca',
            'use_cobertura_tinta',
            'cobertura_tinta',
            'use_cuatricomia',
            'use_cyan',
            'use_yellow',
            'use_magenta',
            'use_black',
            'use_color1',
            'use_color2',
            'use_color3',
            'use_color4',
            'color1',
            'color2',
            'color3',
            'color4')
    def _update_insumos(self):
        if self.ancho == 0 or self.largo == 0 or self.cantidad == 0:
            return

        # Copia items insertados automaticamente para luego recalcularlos
        lst_tmp  = []
        for item in self.insumo_ids:
            if item.flag_adicional == True:
                line_dict = {
                    'name'              : item.name,
                    'product_product_id': item.product_product_id.id,
                    'cantidad'          : item.cantidad,
                    'uom_id'            : item.uom_id.id,
                    'costo_unitario'    : item.costo_unitario,
                    'costo_consumo'     : item.costo_consumo,
                    'cost_currency_id'  : item.cost_currency_id.id,
                    'merma'             : item.merma,
                    'incluido_en_ldm'   : item.incluido_en_ldm,
                    'flag_adicional'    : item.flag_adicional,
                }
                lst_tmp.append(line_dict)
                #self.insumo_ids = [(2,item.id)]
        self.insumo_ids = [(5,0)]

        #----------- Sustrato -----------------
        if self.sustrato_id and self.sustrato_id.product_product_id:
            vals = {
                'select_id': 0,
                'product_product_id': self.sustrato_id.product_product_id.id,
                'cost_currency_id'  : self.sustrato_id.product_product_id.currency_id.id,
                'name'              : self.sustrato_id.product_product_id.name,
                'cantidad'          : self.area_ocupada_con_merma,
                'costo_unitario'    : self.sustrato_id.standard_price,
                'costo_consumo'     : self.sustrato_id.standard_price * self.area_ocupada_con_merma,
                'uom_id'            : self.sustrato_id.product_product_id.uom_id.id,
                'merma'             : self.merma_estimada,
                'incluido_en_ldm'   : True,
                'flag_adicional'    : False,
            }
            self.insumo_ids = [(0,0,vals)]

        #----------- Obligatorios --------------
        for lin in self.producto_id.adicional_ids:
            if lin.obligatorio == True:
                vals = self._prepare_vals_generico(lin)
                self.insumo_ids = [(0,0,vals)]

        #----------- Opcionales (Adicionales) --------------
        for lin in self.adicional_ids:
            vals = self._prepare_vals_generico(lin)
            self.insumo_ids = [(0,0,vals)]

#        #--------- Hojas (Richo) ---------
#        if self.use_cortes == False:

        # Consumos obligatorios (NO SE USA)
        for line in self.producto_id.consumo_ids:
            vals = {
                'select_id': 0,
                'product_product_id': line.product_product_id.id,
                'cost_currency_id'  : line.product_product_id.currency_id.id,
                'name'              : line.product_product_id.name,
                'cantidad'          : line.cantidad * self.area_ocupada * (1 + line.merma / 100.0),
                'costo_unitario'    : line.costo_consumo,
                'costo_consumo'     : line.costo_consumo * self.area_ocupada * (1 + line.merma / 100.0),
                'uom_id'            : line.consumo_uom_id.id,
                'merma'             : line.merma,
                'incluido_en_ldm'   : line.incluido_en_ldm,
                'flag_adicional'    : False,
            }
            self.insumo_ids = [(0,0,vals)]

        #------------------ Cintas TTR ---------------------
        # Solo para TTR
        #if self._area_negocio() == '5':
        if self.use_cinta_ttr == True:
            ttr_id = self.producto_id.get_best_ttr(self.ancho_interno)

            if ttr_id:
                # ttr_id.area y self.area_ocupada en m2
                qty                   = self.area_ocupada / ttr_id.area 
                #qty_productos         = ceil(qty) 
                qty_productos_c_merma = ceil(qty * (1 + ttr_id.merma / 100.0)) 

                vals = {
                    'select_id': 0,
                    'product_product_id': ttr_id.product_product_id.id,
                    'cost_currency_id'  : ttr_id.cost_currency_id.id,
                    'name'              : ttr_id.product_product_id.name,
                    'cantidad'          : qty_productos_c_merma,
                    'costo_unitario'    : ttr_id.standard_price,
                    'costo_consumo'     : ttr_id.standard_price * qty_productos_c_merma,
                    'uom_id'            : ttr_id.product_product_id.uom_id.id,
                    'merma'             : ttr_id.merma,
                    'incluido_en_ldm'   : ttr_id.incluido_en_ldm,
                    'flag_adicional'    : False,
                }
                self.insumo_ids = [(0,0,vals)]

        #---------HH's de cada Centro ---------
        for line in self.producto_id.operation_ids:
            if line.incluye_hh:
                if line.hh_type == 'm':
                    if line.metros_x_min > 0:
                        duracion_estimada = (self.longitud_papel / 1000.0) / line.metros_x_min # En minutos
                    else:
                        duracion_estimada = 0
                elif line.hh_type == 'm+m':
                    if line.metros_x_min > 0:
                        duracion_estimada = (self.longitud_papel_con_merma / 1000.0) / line.metros_x_min # En minutos
                    else:
                        duracion_estimada = 0
                elif line.hh_type == 'm2':
                    if line.metros2_x_min > 0:
                        duracion_estimada = self.area_ocupada / line.metros2_x_min # En minutos
                    else:
                        duracion_estimada = 0
                elif line.hh_type == 'm2+m':
                    if line.metros2_x_min > 0:
                        duracion_estimada = self.area_ocupada_con_merma / line.metros2_x_min # En minutos
                    else:
                        duracion_estimada = 0
                elif line.hh_type == 't':
                    # IMPORTANTE. El calculo de HHs de TTR depende que se seleccione use_bujes!!
                    if self.salidas_x_rollo <= 0:
                        duracion_estimada = 0
                    else:
                        time_seg = (line.seg_x_etiqueta * self.cantidad) / self.salidas_x_rollo
                        duracion_estimada = time_seg / 60 # En minutos

                costo = duracion_estimada * line.costs_min
                values = {
                    'select_id': 0,
                    'cost_currency_id': line.cost_currency_id.id, #OK
                    'name'            : 'HH ' + line.name, #OK
                    'cantidad'        : duracion_estimada, #OK
                    'costo_unitario'  : line.costs_min, #OK
                    'costo_consumo'   : costo,#OK
                    'uom_id'          : line.uom_id_de_consumo.id, #OK
                    'merma'           : 0, #OK
                    'incluido_en_ldm' : False,
                    'flag_adicional'  : False,
                }
                self.insumo_ids = [(0,0,values)]

        #----------------- Buje --------------------
        # Solo para productos tipo etiqueta
        if self.use_bujes == True:
            producto = self.buje_id.product_product_id
            if self.buje_id:
                if self.salidas_x_rollo <= 0:
                    self.etiquetas_x_rollo = 0
                    cantidad = 0
                else:
                    self.etiquetas_x_rollo = floor(((self.buje_id.longitud * 1000) / (self.largo + self.gap))*self.salidas_x_rollo)
                    cantidad = ceil(self.cantidad / self.etiquetas_x_rollo)

                vals = {
                    'select_id': 0,
                    'product_product_id': producto.id if producto else None,
                    'cost_currency_id'  : producto.currency_id.id if producto else None,
                    'name'              : self.buje_id.name,
                    'cantidad'          : cantidad,
                    'costo_unitario'    : self.buje_id.standard_price,
                    'costo_consumo'     : cantidad * self.buje_id.standard_price,
                    'uom_id'            : self.buje_id.uom_id.id,
                    'merma'             : 0,
                    'incluido_en_ldm'   : True,
                    'flag_adicional'    : False,
                }
                self.insumo_ids = [(0,0,vals)]
            else:
                self.etiquetas_x_rollo = 0
                self.salidas_x_rollo   = None

        #----------------- Adicionales --------------------
        for line in self.lista_adicionales_ids:
            adicional = line.adicional_id
            vals = self._prepare_vals_generico(adicional)
            nombre = adicional.name
            if adicional.add_data and line.data_text:
                vals['name'] = nombre + '/' + line.data_text

            self.insumo_ids = [(0,0,vals)]


        #--------- Tinta Blanca (Jetrion) Cobertura ---------
        if self.use_tinta_blanca == True and self.use_cobertura_tinta == True:
            valor        = self.cobertura_tinta.valor
            qty          = self.producto_id.tblanca_cantidad
            tipo_calculo = self.producto_id.tblanca_tipo_calculo
            #---- cantidad ----
            if tipo_calculo == 'f':
                cantidad = qty
                costo    = valor
            elif tipo_calculo == 'm2':
                cantidad = qty * self.area_ocupada
                costo = cantidad * valor
            elif tipo_calculo == 'm':
                cantidad = qty * self.longitud_papel
                costo = cantidad * valor
            elif tipo_calculo == 'm2+m':
                cantidad = qty * self.area_ocupada_con_merma
                costo = cantidad * valor
            elif tipo_calculo == 'm+m':
                cantidad = qty * self.longitud_papel_con_merma
                costo = cantidad * valor

            if self.producto_id.product_product_id:
                product_id = self.producto_id.product_product_id.id
            else:
                product_id = None

            vals = {
                #'producto_id': 0,
                'product_product_id': product_id,
                'cost_currency_id'  : self.currency_id.id, # Currency por defecto
                'name'              : str(self.producto_id.tblanca_name) + '/' + str(self.cobertura_tinta.name),
                'cantidad'          : cantidad,
                'costo_unitario'    : self.cobertura_tinta.tblanca_costo_unitario_consumo,
                'costo_consumo'     : costo,
                'uom_id'            : self.producto_id.tblanca_uom_id_de_consumo.id,
                #'merma': 0.0, # por definir
                'incluido_en_ldm'   : True if self.producto_id.product_product_id else False,
                'flag_adicional'    : False,
            }
            self.insumo_ids = [(0,0,vals)]


        #--------- Cuatricomia (Flexo) ---------
        if self.use_cuatricomia == True:
            count_colores = 0
            if self.use_barniz and self.producto_id.barniz:
                vals = self._prepare_vals_generico(self.producto_id.barniz)
                self.insumo_ids = [(0,0,vals)]
                count_colores = count_colores + 1
            if self.use_cyan and self.producto_id.color_cyan:
                vals = self._prepare_vals_generico(self.producto_id.color_cyan)
                self.insumo_ids = [(0,0,vals)]
                count_colores = count_colores + 1
            if self.use_black and self.producto_id.color_black:
                vals = self._prepare_vals_generico(self.producto_id.color_black)
                self.insumo_ids = [(0,0,vals)]
                count_colores = count_colores + 1
            if self.use_magenta and self.producto_id.color_magenta:
                vals = self._prepare_vals_generico(self.producto_id.color_magenta)
                self.insumo_ids = [(0,0,vals)]
                count_colores = count_colores + 1
            if self.use_yellow and self.producto_id.color_yellow:
                vals = self._prepare_vals_generico(self.producto_id.color_yellow)
                self.insumo_ids = [(0,0,vals)]
                count_colores = count_colores + 1
            if self.use_color1 and self.producto_id.color1:
                vals = self._prepare_vals_generico(self.producto_id.color1)
                vals['name'] = vals['name'] + ' / ' + str(self.color1)
                self.insumo_ids = [(0,0,vals)]
                count_colores = count_colores + 1
            if self.use_color2 and self.producto_id.color2:
                vals = self._prepare_vals_generico(self.producto_id.color2)
                vals['name'] = vals['name'] + ' / ' + str(self.color2)
                self.insumo_ids = [(0,0,vals)]
                count_colores = count_colores + 1
            if self.use_color3 and self.producto_id.color3:
                vals = self._prepare_vals_generico(self.producto_id.color3)
                vals['name'] = vals['name'] + ' / ' + str(self.color3)
                self.insumo_ids = [(0,0,vals)]
                count_colores = count_colores + 1
            if self.use_color4 and self.producto_id.color4:
                vals = self._prepare_vals_generico(self.producto_id.color4)
                vals['name'] = vals['name'] + ' / ' + str(self.color4)
                self.insumo_ids = [(0,0,vals)]
                count_colores = count_colores + 1

            #Cliches
            if count_colores > 0:
                factor = self.factor_uom(self.producto_id.cliche_uom_id_de_consumo, self.env.ref('cotizador_l10n_cl.uom_square_mm'))

                #costo_unitario = self.producto_id.cliche_uom_id_de_consumo._compute_quantity(self.producto_id.cliche_costo_unitario_consumo,self.env.ref('cotizador_l10n_cl.uom_square_mm'))
                costo_unitario = self.producto_id.cliche_costo_unitario_consumo * factor

                costo = count_colores * (self.z_ingreso * self.engranaje - 9.889) * self.ancho_bobina * costo_unitario
                vals = {
                    #'producto_id': 0,
                    'cost_currency_id': self.currency_id.id, # Currency por defecto
                    'name'            : 'CLICHE',
                    'cantidad'        : count_colores,
                    'costo_unitario'  : self.producto_id.cliche_costo_unitario_consumo,
                    'costo_consumo'   : costo,
                    'uom_id'          : self.producto_id.cliche_uom_id_de_consumo.id,
                    #'merma': 0.0, # por definir
                    'incluido_en_ldm' : False,
                    'flag_adicional'  : False,
                }
                self.insumo_ids = [(0,0,vals)]


        # Reingresa items creados por el usuario
        for lst in lst_tmp:
            self.insumo_ids = [(0,0,lst)]

    def factor_uom(self, uom_origen, uom_destino):
        # Lleva a uom de referencia
        if uom_origen.uom_type == 'reference':
            factor = 1
        elif uom_origen.uom_type == 'bigger':
            factor = uom_origen.factor_inv
        else:
            factor = uom_origen.factor

        # Calcula en uom de destino
        if uom_destino.uom_type == 'reference':
            factor2 = 1
        elif uom_destino.uom_type == 'bigger':
            factor2 = uom_destino.factor
        else:
            factor2 = uom_destino.factor_inv

        return factor * factor2
        #rec.tblanca_costo_unitario_consumo = rec.tblanca_standard_price * factor



    def add_product(self):
        self._update_insumos() # Se vuelve a llamar. Los valores llegaban en 0.
        product = self.create_product()
        if product:
            product.product_tmpl_id.gen_cotizador = True
            # Campos necesario para calcular precio (tarifa)
            product.product_tmpl_id.producto_id   = self.producto_id
            product.product_tmpl_id.sustrato_id   = self.sustrato_id
            product.product_tmpl_id.area_ocupada_con_merma = self.area_ocupada_con_merma
            product.product_tmpl_id.list_price = product.product_tmpl_id._get_tarifa_pricelist_price()
            product.list_price = product.product_tmpl_id.list_price

            ############### FABRICACION ###################
            #------- Rutas de producto (MTO y Fabricar) --------
            stock_id = self.env.ref('stock.route_warehouse0_mto').id
            mrp_id   = self.env.ref('mrp.route_warehouse0_manufacture').id
            product.route_ids = [(5,0)] + [(4,stock_id),(4,mrp_id)]

            #---------------- Crear BoM ------------------------
            vals = {
                'product_tmpl_id'    : product.product_tmpl_id.id,
                'type'               : 'normal', # Fabricar este producto
                'product_qty'        : self.cantidad,
                'analytic_account_id': self.producto_id.analytic_account_id.id or None, # Actualiza cta analitica en SO line
            }
            mrp = self.env["mrp.bom"].create(vals)

            list_parametros = {'content':[]}
            count_parametros = 0
            #self._update_insumos() # Se vuelve a llamar. Los valores llegaban en 0.
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

            values = {
                #"product_id": 21, #ID
                #"product_id": self.sustrato_id.product_id.id, #ID
                "product_tmpl_id": product.product_tmpl_id.id, #ID
                "product_qty": self.cantidad, #Cantidad a producir=Cantidad en BOM
                #"bom_id": mrp.id
            }
            # Comentado por ahora
            #mrp.bom_line_ids = [(0,0,values)]

            for operation in self.producto_id.operation_ids:
                values = {
                    'name': operation.name,
                    'workcenter_id': operation.workcenter_id.id, #ID
                    'bom_id': mrp.id, #ID
                    #Agregar resto de campos de mrp.routing.workcenter.tmp
                    'worksheet_type': 'text',
                    #JCR prueba de formato
                    'note': self._get_html_parametros(list_parametros),#product.lista_parametros,
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
                #"list_price"     : self.precio_unitario,
                "uom_id"         : self.product_uom_id.id,
            }
            product = self.env["product.product"].create(vals)
            return product
        else:
            return False

#    def genera_descripcion(self):
#        texto = ""
#        if self.buje_id:
#            texto =  "BUJE: " + self.buje_id.name +"<br>"
#        if self.aisa_id:
#            texto += "AISA: " + self.aisa_id.name +"<br>"
#        if self.adhesivo_id:
#            texto += "ADHESIVO: " + self.adhesivo_id.name +"<br>"
#        if self.datos_adicionales:
#            texto += "DATOS ADICIONALES:<br>" + self.datos_adicionales +"<br>"
#
#        return texto


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


    def _get_html_parametros(self, parametros):
        data = parametros['data']

        html = "<table>"
        html = html + "<tr><td><strong>Largo</strong></td><td>" + str(data['largo']) + "</td></tr>"
        html = html + "<tr><td><strong>Ancho</strong></td><td>" + str(data['ancho']) + "</td></tr>"
        html = html + "<tr><td><strong>Comentarios</strong></td><td><textarea rows='4' cols='50' readonly>" + str(data['datos_adicionales']) + "</textarea></td></tr>"
        if data['aisa']:
            html = html + "<tr><td><strong>AISA</strong></td><td>" + data['aisa'] + "</td></tr>"
        html = html + "</table>"

        html = html + "<table>"
        html = html + "<tr><td><strong>Producto</strong></td><td><strong>Cantidad</strong></td><td><strong>UdM</strong></td></tr>"
        for item in parametros['content']:
            html = html + "<tr>"
            html = html + "<td>" + item['producto'] + "</td>"
            html = html + "<td>" + str(item['cantidad']) + "</td>"
            html = html + "<td>" + item['uom'] + "</td>"
            html = html + "</tr>"
        html = html + "</table>"

        return html
