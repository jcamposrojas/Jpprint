#
# v.1.1 20220717 Cambio en metodologia web scraping. Vanguard.
#
from odoo import api, fields, models, tools, _
from urllib.request import urlopen
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import requests
import re

import locale

locale._override_localeconv["thousands_sep"] = "."
locale._override_localeconv["decimal_point"] = ","


URL_PREVIRED = "https://www.previred.com/web/previred/indicadores-previsionales"

_logger = logging.getLogger(__name__)

MONTH_LIST= [('1', 'Enero'), 
        ('2', 'Febrero'), ('3', 'Marzo'), 
        ('4', 'Abril'), ('5', 'Mayo'), 
        ('6', 'Junio'), ('7', 'Julio'), 
        ('8', 'Agosto'), ('9', 'Septiembre'), 
        ('10', 'Octubre'), ('11', 'Noviembre'),
        ('12', 'Diciembre')]

STATES = {'draft': [('readonly', False)]}

class hr_indicadores_previsionales(models.Model):
    _name = 'hr.indicadores'
    _description = 'Indicadores Previsionales'

    name = fields.Char('Nombre')
    state = fields.Selection([
        ('draft','Borrador'),
        ('done','Validado'),
        ], string=u'Estado', readonly=True, default='draft')
    asignacion_familiar_primer = fields.Float('Asignación Familiar Tramo 1', readonly=True, states=STATES,
        help="Asig Familiar Primer Tramo")
    asignacion_familiar_segundo = fields.Float('Asignación Familiar Tramo 2', readonly=True, states=STATES,
        help="Asig Familiar Segundo Tramo")
    asignacion_familiar_tercer = fields.Float('Asignación Familiar Tramo 3', readonly=True, states=STATES,
        help="Asig Familiar Tercer Tramo")
    asignacion_familiar_monto_a = fields.Float( 'Monto Tramo Uno', readonly=True, states=STATES, help="Monto A")
    asignacion_familiar_monto_b = fields.Float( 'Monto Tramo Dos', readonly=True, states=STATES, help="Monto B")
    asignacion_familiar_monto_c = fields.Float( 'Monto Tramo Tres', readonly=True, states=STATES, help="Monto C")
    contrato_plazo_fijo_empleador = fields.Float( 'Contrato Plazo Fijo Empleador', readonly=True, states=STATES,
        help="Contrato Plazo Fijo Empleador")
    contrato_plazo_fijo_trabajador = fields.Float( 'Contrato Plazo Fijo Trabajador', readonly=True, states=STATES,
        help="Contrato Plazo Fijo Trabajador")    
    contrato_plazo_indefinido_empleador = fields.Float( 'Contrato Plazo Indefinido Empleador', readonly=True, states=STATES,
        help="Contrato Plazo Fijo")
    contrato_plazo_indefinido_empleador_otro = fields.Float( 'Contrato Plazo Indefinido Empleador 11 anos o mas', 
        readonly=True, states=STATES, help="Contrato Plazo Indefinido 11 anos Empleador")
    contrato_plazo_indefinido_trabajador_otro = fields.Float( 'Contrato Plazo Indefinido Trabajador 11 anos o mas', 
        readonly=True, states=STATES, help="Contrato Plazo Indefinido 11 anos Trabajador")
    contrato_plazo_indefinido_trabajador = fields.Float( 'Contrato Plazo Indefinido Trabajador', readonly=True, states=STATES,
        help="Contrato Plazo Indefinido Trabajador")
    caja_compensacion  = fields.Float( 'Caja Compensación', readonly=True, states=STATES, help="Caja de Compensacion")
    deposito_convenido = fields.Float( 'Deposito Convenido', readonly=True, states=STATES, help="Deposito Convenido")
    fonasa = fields.Float('Fonasa', readonly=True, states=STATES, help="Fonasa")
    mutual_seguridad = fields.Float( 'Mutualidad', readonly=True, states=STATES, help="Mutual de Seguridad")
    isl = fields.Float( 'ISL', readonly=True, states=STATES, help="Instituto de Seguridad Laboral")
    pensiones_ips = fields.Float( 'Pensiones IPS', readonly=True, states=STATES, help="Pensiones IPS")
    sueldo_minimo = fields.Float( 'Trab. Dependientes e Independientes', readonly=True, states=STATES, help="Sueldo Minimo")
    sueldo_minimo_otro = fields.Float( 'Menores de 18 y Mayores de 65:', readonly=True, states=STATES,
        help="Sueldo Mínimo para Menores de 18 y Mayores a 65")
    tasa_afp_cuprum  = fields.Float( 'Cuprum', readonly=True, states=STATES, help="Tasa AFP Cuprum")
    tasa_afp_capital = fields.Float( 'Capital', readonly=True, states=STATES, help="Tasa AFP Capital")
    tasa_afp_provida = fields.Float( 'ProVida', readonly=True, states=STATES, help="Tasa AFP Provida")
    tasa_afp_modelo  = fields.Float( 'Modelo', readonly=True, states=STATES, help="Tasa AFP Modelo")
    tasa_afp_planvital = fields.Float( 'PlanVital', readonly=True, states=STATES, help="Tasa AFP PlanVital")
    tasa_afp_habitat = fields.Float( 'Habitat',  help="Tasa AFP Habitat")
    tasa_afp_uno = fields.Float( 'Uno', help="Tasa AFP Uno")
    tasa_sis_cuprum  = fields.Float('SIS', readonly=True, states=STATES, help="Tasa SIS Cuprum")
    tasa_sis_capital = fields.Float( 'SIS', readonly=True, states=STATES, help="Tasa SIS Capital")
    tasa_sis_provida = fields.Float( 'SIS', readonly=True, states=STATES, help="Tasa SIS Provida")
    tasa_sis_planvital = fields.Float( 'SIS', readonly=True, states=STATES, help="Tasa SIS PlanVital")
    tasa_sis_habitat = fields.Float( 'SIS', readonly=True, states=STATES, help="Tasa SIS Habitat")
    tasa_sis_modelo  = fields.Float( 'SIS',  help="Tasa SIS Modelo")
    tasa_sis_uno = fields.Float( 'SIS', help="Tasa SIS Uno")
    tasa_independiente_cuprum = fields.Float( 'SIS', readonly=True, states=STATES, help="Tasa Independientes Cuprum")
    tasa_independiente_capital = fields.Float( 'SIS', readonly=True, states=STATES, help="Tasa Independientes Capital")
    tasa_independiente_provida = fields.Float( 'SIS', readonly=True, states=STATES, help="Tasa Independientes Provida")
    tasa_independiente_planvital = fields.Float( 'SIS', readonly=True, states=STATES, help="Tasa Independientes PlanVital")
    tasa_independiente_habitat = fields.Float( 'SIS', readonly=True, states=STATES, help="Tasa Independientes Habitat")
    tasa_independiente_modelo = fields.Float( 'SIS',  help="Tasa Independientes Modelo")
    tasa_independiente_uno = fields.Float( 'SIS', help="Tasa Independientes Uno")
    tope_anual_apv = fields.Float( 'Tope Anual APV', readonly=True, states=STATES, help="Tope Anual APV")
    tope_mensual_apv = fields.Float( 'Tope Mensual APV', readonly=True, states=STATES, help="Tope Mensual APV")
    tope_imponible_afp = fields.Float( 'Tope imponible AFP', readonly=True, states=STATES, help="Tope Imponible AFP")
    tope_imponible_ips = fields.Float( 'Tope Imponible IPS', readonly=True, states=STATES, help="Tope Imponible IPS")
    tope_imponible_salud = fields.Float( 'Tope Imponible Salud', readonly=True, states=STATES,)
    tope_imponible_seguro_cesantia = fields.Float( 'Tope Imponible Seguro Cesantía', readonly=True, states=STATES,
        help="Tope Imponible Seguro de Cesantía")
    uf  = fields.Float('UF', required=True, readonly=True, states=STATES, help="UF fin de Mes")
    utm = fields.Float('UTM', required=True, readonly=True, states=STATES, help="UTM Fin de Mes")
    uta = fields.Float('UTA', readonly=True, states=STATES, help="UTA Fin de Mes")
    uf_otros = fields.Float( 'UF Otros', readonly=True, states=STATES, help="UF Seguro Complementario")
    mutualidad_id = fields.Many2one('hr.mutual', 'MUTUAL', readonly=True, states=STATES)
    ccaf_id = fields.Many2one('hr.ccaf', 'CCAF', readonly=True, states=STATES)
    month = fields.Selection(MONTH_LIST, string='Mes', required=True, readonly=True, states=STATES)
    year = fields.Integer('Año', required=True, default=datetime.now().strftime('%Y'), readonly=True, states=STATES)
    gratificacion_legal = fields.Boolean('Gratificación L. Manual', readonly=True, states=STATES)
    mutual_seguridad_bool = fields.Boolean('Mutual Seguridad', default=True, readonly=True, states=STATES)
    ipc = fields.Float('IPC',  required=True, readonly=True, states=STATES, help="Indice de Precios al Consumidor (IPC)")
    
    def action_done(self):
        self.write({'state': 'done'})
        return True
    
    def action_draft(self):
        self.write({'state': 'draft'})
        return True

    @api.onchange('month')
    def get_name(self):
        self.name = str(self.month).replace('10', 'Octubre').replace('11', 'Noviembre').replace('12', 'Diciembre').replace('1', 'Enero').replace('2', 'Febrero').replace('3', 'Marzo').replace('4', 'Abril').replace('5', 'Mayo').replace('6', 'Junio').replace('7', 'Julio').replace('8', 'Agosto').replace('9', 'Septiembre') + " " + str(self.year)

    def find_between_r(self, s, first, last ):
        try:
            start = s.rindex( first ) + len( first )
            end = s.rindex( last, start )
            return s[start:end]
        except ValueError:
            return ""

    def find_month(self, s):
        if s == '1':
            return 'Enero'
        if s == '2':
            return 'Febrero'
        if s == '3':
            return 'Marzo'
        if s == '4':
            return 'Abril'
        if s == '5':
            return 'Mayo'
        if s == '6':
            return 'Junio'
        if s == '7':
            return 'Julio'
        if s == '8':
            return 'Agosto'
        if s == '9':
            return 'Septiembre'
        if s == '10':
            return 'Octubre'
        if s == '11':
            return 'Noviembre'
        if s == '12':
            return 'Diciembre'


    def update_document(self):
        #self.update_date = datetime.today()
        try:
            url = 'https://www.previred.com/web/previred/indicadores-previsionales'
            page = urlopen(url)
            html_bytes = page.read()
            html = html_bytes.decode("utf-8")
            brute = re.findall("\$ [\d\.,]+<|>[\d]+\.[\d\.]+<|>[\d,]+%<|>[\d,]+% R\.I\. ?<", html)
            pure = []
            for item in brute:
                pure.append(float((re.search("[\d\.,]+", item)[0]).replace('.','').replace(',','.')))
        except ValueError:
            return ""
        def uf_convert(cad):
            return round(cad / self.uf, 2)
        try:
            new_ind = self._hrIndPrevired()
            # UF
            self.uf = new_ind['UF'][new_ind['MES_UTM']]

            # 1 UTM
            self.utm = new_ind['UTM']

            # 1 UTA
            self.uta = new_ind['UTA']

            # 3 RENTAS TOPES IMPONIBLES (UF)
            self.tope_imponible_afp             = new_ind['RENTAS_TOPE_AFP'][0]
            self.tope_imponible_ips             = new_ind['RENTAS_TOPE_IPS'][0]
            self.tope_imponible_seguro_cesantia = new_ind['RENTAS_TOPE_SEGURO'][0]

            # 4 RENTAS MINIMAS IMPONIBLES
            self.sueldo_minimo      = new_ind['RENTAS_MINIMA_DEP_INDEP'][0]
            self.sueldo_minimo_otro = new_ind['RENTAS_MINIMA_18_Y_65'][0]

            # Ahorro Previsional Voluntario (UF)
            self.tope_mensual_apv = new_ind['APV_TOPE_MENSUAL'][0]
            self.tope_anual_apv   = new_ind['APV_TOPE_ANUAL'][0]

            # 5 DEPÓSITO CONVENIDO (UF)
            self.deposito_convenido = new_ind['DEPOSITO_CONVENIDO_TOPE_ANUAL'][0]

            # 6 SEGURO DE CESANTÍA (AFC)
            self.contrato_plazo_indefinido_empleador      = new_ind['SEGURO_CESANTIA_PLAZO_INDEF'][0]
            self.contrato_plazo_indefinido_trabajador     = new_ind['SEGURO_CESANTIA_PLAZO_INDEF'][1]
            self.contrato_plazo_fijo_empleador            = new_ind['SEGURO_CESANTIA_PLAZO_FIJO']
            self.contrato_plazo_indefinido_empleador_otro = new_ind['SEGURO_CESANTIA_11_ANNOS']

            # 7 ASIGNACIÓN FAMILIAR
            self.asignacion_familiar_monto_a = new_ind['ASIGNACION_FAMILIAR_A'][0]
            self.asignacion_familiar_monto_b = new_ind['ASIGNACION_FAMILIAR_B'][0]
            self.asignacion_familiar_monto_c = new_ind['ASIGNACION_FAMILIAR_C'][0]

            self.asignacion_familiar_primer  = new_ind['ASIGNACION_FAMILIAR_A'][1]
            self.asignacion_familiar_segundo = new_ind['ASIGNACION_FAMILIAR_B'][1]
            self.asignacion_familiar_tercer  = new_ind['ASIGNACION_FAMILIAR_C'][1]

            # 8 TASA COTIZACIÓN OBLIGATORIO AFP
            self.tasa_afp_capital           = new_ind['TASA_CAPITAL'][0]
            self.tasa_sis_capital           = new_ind['TASA_CAPITAL'][1]
            self.tasa_independiente_capital = new_ind['TASA_CAPITAL'][2]

            self.tasa_afp_cuprum           = new_ind['TASA_CUPRUM'][0]
            self.tasa_sis_cuprum           = new_ind['TASA_CUPRUM'][1]
            self.tasa_independiente_cuprum = new_ind['TASA_CUPRUM'][2]

            self.tasa_afp_habitat           = new_ind['TASA_HABITAT'][0]
            self.tasa_sis_habitat           = new_ind['TASA_HABITAT'][1]
            self.tasa_independiente_habitat = new_ind['TASA_HABITAT'][2]

            self.tasa_afp_planvital           = new_ind['TASA_PLANVITAL'][0]
            self.tasa_sis_planvital           = new_ind['TASA_PLANVITAL'][1]
            self.tasa_independiente_planvital = new_ind['TASA_PLANVITAL'][2]

            self.tasa_afp_provida           = new_ind['TASA_PROVIDA'][0]
            self.tasa_sis_provida           = new_ind['TASA_PROVIDA'][1]
            self.tasa_independiente_provida = new_ind['TASA_PROVIDA'][2]

            self.tasa_afp_modelo           = new_ind['TASA_MODELO'][0]
            self.tasa_sis_modelo           = new_ind['TASA_MODELO'][1]
            self.tasa_independiente_modelo = new_ind['TASA_MODELO'][2]

            self.tasa_afp_uno           = new_ind['TASA_UNO'][0]
            self.tasa_sis_uno           = new_ind['TASA_UNO'][1]
            self.tasa_independiente_uno = new_ind['TASA_UNO'][2]
        except ValueError:
            return ""



    def _hrIndPrevired(self):
        page = requests.get(URL_PREVIRED)
        if page.status_code != 200:
            return None;

        indicadores = {
            'UF':{},
            'UTM':0.0,
            'UTA':[],
            'MES_UTM':'',
            'RENTAS_TOPE_AFP':[],
            'RENTAS_TOPE_IPS':[],
            'RENTAS_TOPE_SEGURO':[],
            'RENTAS_MINIMA_DEP_INDEP':[],
            'RENTAS_MINIMA_18_Y_65':[],
            'RENTAS_MINIMA_CASA_PARTICULAR':[],
            'RENTAS_MINIMA_NO_REMU':[],
            'APV_TOPE_MENSUAL':[],
            'APV_TOPE_ANUAL':[],
            'DEPOSITO_CONVENIDO_TOPE_ANUAL':[],
            'SEGURO_CESANTIA_PLAZO_INDEF':[],
            'SEGURO_CESANTIA_PLAZO_FIJO':[],
            'SEGURO_CESANTIA_11_ANNOS':[],
            'SEGURO_CESANTIA_CASA_PARTICULAR':[],
            'DISTRIBUCION_7P_CCAF':[],
            'DISTRIBUCION_7P_FONASA':[],
            'TASA_CAPITAL':[],
            'TASA_CUPRUM':[],
            'TASA_HABITAT':[],
            'TASA_PLANVITAL':[],
            'TASA_PROVIDA':[],
            'TASA_MODELO':[],
            'TASA_UNO':[],
            'ASIGNACION_FAMILIAR_A':[],
            'ASIGNACION_FAMILIAR_B':[],
            'ASIGNACION_FAMILIAR_C':[],
            'ASIGNACION_FAMILIAR_D':[],
            'COTIZACION_TRAB_PESADO':[],
            'COTIZACION_TRAB_MENOS_PESADO':[],
        }

        re_monto_patron     = re.compile(r'(?:\$\s*)(\d{1,3}(?:\.\d{3})*(?:,\d+)?)|-')
        re_monto_porcentaje = re.compile(r'>\s*((?:\d+)(?:,\d+)?)\s*%\s*(?:R\.I\.)?\s*<')

        soup = BeautifulSoup(page.content, "html.parser")

        div_journal = soup.find_all('div',class_='journal-content-article')
        for div in div_journal:
            s = div.find_all(class_='encabezado_tabla_ind')
            for f in s:
                #print('-'+f.get_text()+'-')
                if f.get_text() == 'VALOR UF':
                    #print(div)
                    for tr in div.find_all('tr'):
                        if f.get_text().strip() != tr.get_text().strip():
                            b = re.findall(r'al\s+(\d+)\s+de\s+(\w+)\s+(\d+)',str(tr),re.IGNORECASE)
                            uf = re_monto_patron.findall(str(tr))
                            indicadores['UF'][b[0][1].upper()] = locale.atof(uf[0])
                elif f.get_text() == 'RENTAS TOPES IMPONIBLES':
                    for tr in div.find_all('tr'):
                        if f.get_text().strip() != tr.get_text().strip():
                            b = re.findall(r'ara\s+afiliados\s+a\s+una\s+AFP\s+\(((?:\d+)(?:,\d+)?)\s+UF\)',str(tr),re.IGNORECASE)
                            if b:
                                valor_clp = re_monto_patron.findall(str(tr))
                                indicadores['RENTAS_TOPE_AFP'] = [locale.atof(b[0]), locale.atof(valor_clp[0])]

                            b = re.findall(r'ara\s+afiliados\s+al\s+IPS\s+\(ex\s+INP\)\s+\(((?:\d+)(?:,\d+)?)\s+UF\)',str(tr),re.IGNORECASE)
                            if b:
                                valor_clp = re_monto_patron.findall(str(tr))
                                indicadores['RENTAS_TOPE_IPS'] = [locale.atof(b[0]), locale.atof(valor_clp[0])]
                            b = re.findall(r'ara\s+seguro\s+de\s+Cesantía\s+\(((?:\d+)(?:,\d+)?)\s+UF\)',str(tr),re.IGNORECASE)
                            if b:
                                valor_clp = re_monto_patron.findall(str(tr))
                                indicadores['RENTAS_TOPE_SEGURO'] = [locale.atof(b[0]), locale.atof(valor_clp[0])]
                elif f.get_text() == 'RENTAS MÍNIMAS IMPONIBLES':
                    for tr in div.find_all('tr'):
                        if f.get_text().strip() != tr.get_text().strip():
                            b = re.findall(r'Trab.\s+Dependientes\s+e\s+Independientes',str(tr),re.IGNORECASE)
                            if b:
                                valor_clp = re_monto_patron.findall(str(tr))
                                indicadores['RENTAS_MINIMA_DEP_INDEP'] = [locale.atof(valor_clp[0])]
                            b = re.findall(r'Menores\s+de\s+18\s+y\s+Mayores\s+de\s+65',str(tr),re.IGNORECASE)
                            if b:
                                valor_clp = re_monto_patron.findall(str(tr))
                                indicadores['RENTAS_MINIMA_18_Y_65'] = [locale.atof(valor_clp[0])]
                            b = re.findall(r'Trabajadores\s+de\s+Casa\s+Particular',str(tr),re.IGNORECASE)
                            if b:
                                valor_clp = re_monto_patron.findall(str(tr))
                                indicadores['RENTAS_MINIMA_CASA_PARTICULAR'] = [locale.atof(valor_clp[0])]
                            b = re.findall(r'Para\s+fines\s+no\s+remuneracionales',str(tr),re.IGNORECASE)
                            if b:
                                valor_clp = re_monto_patron.findall(str(tr))
                                indicadores['RENTAS_MINIMA_NO_REMU'] = [locale.atof(valor_clp[0])]
                elif f.get_text() == 'AHORRO PREVISIONAL VOLUNTARIO (APV)':
                    for tr in div.find_all('tr'):
                        if f.get_text().strip() != tr.get_text().strip():
                            b = re.findall(r'Tope\s+Mensual\s+\(((?:\d+)(?:,\d+)?)\s+UF\)',str(tr),re.IGNORECASE)
                            if b:
                                valor_clp = re_monto_patron.findall(str(tr))
                                indicadores['APV_TOPE_MENSUAL'] = [locale.atof(b[0]), locale.atof(valor_clp[0])]
                            b = re.findall(r'Tope\s+Anual\s+\(((?:\d+)(?:,\d+)?)\s+UF\)',str(tr),re.IGNORECASE)
                            if b:
                                valor_clp = re_monto_patron.findall(str(tr))
                                indicadores['APV_TOPE_ANUAL'] = [locale.atof(b[0]), locale.atof(valor_clp[0])]
                elif f.get_text() == 'DEPÓSITO CONVENIDO':
                    for tr in div.find_all('tr'):
                        if f.get_text().strip() != tr.get_text().strip():
                            b = re.findall(r'Tope\s+Anual\s+\(((?:\d+)(?:,\d+)?)\s+UF\)',str(tr),re.IGNORECASE)
                            if b:
                                valor_clp = re_monto_patron.findall(str(tr))
                                indicadores['DEPOSITO_CONVENIDO_TOPE_ANUAL'] = [locale.atof(b[0]), locale.atof(valor_clp[0])]
                elif f.get_text() == 'SEGURO DE CESANTÍA (AFC)':
                    for tr in div.find_all('tr'):
                        if f.get_text().strip() != tr.get_text().strip():
                            b = re.findall(r'Plazo\s+Indefinido\s*<',str(tr),re.IGNORECASE)
                            if b:
                                valor_clp = re_monto_porcentaje.findall(str(tr))
                                indicadores['SEGURO_CESANTIA_PLAZO_INDEF']=[locale.atof(valor_clp[0]),locale.atof(valor_clp[1])]
                            b = re.findall(r'Plazo\s+Fijo\s*<',str(tr),re.IGNORECASE)
                            if b:
                                valor_clp = re_monto_porcentaje.findall(str(tr))
                                indicadores['SEGURO_CESANTIA_PLAZO_FIJO'] = locale.atof(valor_clp[0])
                            b = re.findall(r'Plazo\s+Indefinido\s+11\s+a',str(tr),re.IGNORECASE)
                            if b:
                                valor_clp = re_monto_porcentaje.findall(str(tr))
                                indicadores['SEGURO_CESANTIA_11_ANNOS'] = locale.atof(valor_clp[0])
                            b = re.findall(r'Trabajador\s+de\s+Casa\s+Particular',str(tr),re.IGNORECASE)
                            if b:
                                valor_clp = re_monto_porcentaje.findall(str(tr))
                                indicadores['SEGURO_CESANTIA_CASA_PARTICULAR'] = locale.atof(valor_clp[0])
                elif f.get_text() == 'DISTRIBUCIÓN DEL 7% SALUD, PARA EMPLEADORES AFILIADOS A CCAF (*)':
                    for tr in div.find_all('tr'):
                        if f.get_text().strip() != tr.get_text().strip():
                            b = re.findall(r'>\s*CCAF\s*<',str(tr),re.IGNORECASE)
                            if b:
                                valor_clp = re_monto_porcentaje.findall(str(tr))
                                indicadores['DISTRIBUCION_7P_CCAF'] = valor_clp
                            b = re.findall(r'>\s*FONASA\s*<',str(tr),re.IGNORECASE)
                            if b:
                                valor_clp = re_monto_porcentaje.findall(str(tr))
                                indicadores['DISTRIBUCION_7P_FONASA'] = valor_clp
                elif f.get_text() == 'TASA COTIZACIÓN OBLIGATORIO AFP':
                    for tr in div.find_all('tr'):
                        if f.get_text().strip() != tr.get_text().strip():
                            b = re.findall(r'>\s*Capital\s*<',str(tr),re.IGNORECASE)
                            if b:
                                valor_clp = re_monto_porcentaje.findall(str(tr))
                                indicadores['TASA_CAPITAL'] = [
                                        locale.atof(valor_clp[0]),
                                        locale.atof(valor_clp[1]),
                                        locale.atof(valor_clp[2])]
                            b = re.findall(r'>\s*Cuprum\s*<',str(tr),re.IGNORECASE)
                            if b:
                                valor_clp = re_monto_porcentaje.findall(str(tr))
                                indicadores['TASA_CUPRUM'] = [
                                        locale.atof(valor_clp[0]),
                                        locale.atof(valor_clp[1]),
                                        locale.atof(valor_clp[2])]
                            b = re.findall(r'>\s*Habitat\s*<',str(tr),re.IGNORECASE)
                            if b:
                                valor_clp = re_monto_porcentaje.findall(str(tr))
                                indicadores['TASA_HABITAT'] = [
                                        locale.atof(valor_clp[0]),
                                        locale.atof(valor_clp[1]),
                                        locale.atof(valor_clp[2])]
                            b = re.findall(r'>\s*PlanVital\s*<',str(tr),re.IGNORECASE)
                            if b:
                                valor_clp = re_monto_porcentaje.findall(str(tr))
                                indicadores['TASA_PLANVITAL'] = [
                                        locale.atof(valor_clp[0]),
                                        locale.atof(valor_clp[1]),
                                        locale.atof(valor_clp[2])]
                            b = re.findall(r'>\s*ProVida\s*<',str(tr),re.IGNORECASE)
                            if b:
                                valor_clp = re_monto_porcentaje.findall(str(tr))
                                indicadores['TASA_PROVIDA'] = [
                                        locale.atof(valor_clp[0]),
                                        locale.atof(valor_clp[1]),
                                        locale.atof(valor_clp[2])]
                            b = re.findall(r'>\s*Modelo\s*<',str(tr),re.IGNORECASE)
                            if b:
                                valor_clp = re_monto_porcentaje.findall(str(tr))
                                indicadores['TASA_MODELO'] = [
                                        locale.atof(valor_clp[0]),
                                        locale.atof(valor_clp[1]),
                                        locale.atof(valor_clp[2])]
                            b = re.findall(r'>\s*Uno\s*<',str(tr),re.IGNORECASE)
                            if b:
                                valor_clp = re_monto_porcentaje.findall(str(tr))
                                indicadores['TASA_UNO'] = [
                                        locale.atof(valor_clp[0]),
                                        locale.atof(valor_clp[1]),
                                        locale.atof(valor_clp[2])]
                elif f.get_text() == 'ASIGNACIÓN FAMILIAR':
                    for tr in div.find_all('tr'):
                        if f.get_text().strip() != tr.get_text().strip():
                            b = re.findall(r'>\s*1\s+\(\s*A\s*\)\s*<',str(tr),re.IGNORECASE)
                            if b:
                                valor_clp = re_monto_patron.findall(str(tr))
                                indicadores['ASIGNACION_FAMILIAR_A'] = [locale.atof(valor_clp[0]),locale.atof(valor_clp[-1])]
                            b = re.findall(r'>\s*2\s+\(\s*B\s*\)\s*<',str(tr),re.IGNORECASE)
                            if b:
                                valor_clp = re_monto_patron.findall(str(tr))
                                indicadores['ASIGNACION_FAMILIAR_B'] = [locale.atof(valor_clp[0]),locale.atof(valor_clp[-1])]
                            b = re.findall(r'>\s*3\s+\(\s*C\s*\)\s*<',str(tr),re.IGNORECASE)
                            if b:
                                valor_clp = re_monto_patron.findall(str(tr))
                                indicadores['ASIGNACION_FAMILIAR_C'] = [locale.atof(valor_clp[0]),locale.atof(valor_clp[-1])]
                            b = re.findall(r'>\s*4\s+\(\s*D\s*\)\s*<',str(tr),re.IGNORECASE)
                            if b:
                                valor_clp = re_monto_patron.findall(str(tr))
                                #indicadores['ASIGNACION_FAMILIAR_D'] = [locale.atof(valor_clp[0])]
                elif f.get_text().strip() == 'COTIZACIÓN PARA TRABAJOS PESADOS':
                    for tr in div.find_all('tr'):
                        if f.get_text().strip() != tr.get_text().strip():
                            b = re.findall(r'>\s*Trabajo\s+pesado\s*<',str(tr),re.IGNORECASE)
                            if b:
                                valor_clp = re_monto_porcentaje.findall(str(tr))
                                indicadores['COTIZACION_TRAB_PESADO'] = valor_clp
                            b = re.findall(r'>\s*Trabajo\s+menos\s+pesado\s*<',str(tr),re.IGNORECASE)
                            if b:
                                valor_clp = re_monto_porcentaje.findall(str(tr))
                                indicadores['COTIZACION_TRAB_MENOS_PESADO'] = valor_clp
                elif f.get_text().strip() == 'VALOR UTM UTA':
                    for tr in div.find_all('tr'):
                        if f.get_text().strip() != tr.get_text().strip():
                            #print(str(tr))
                            cont = 0
                            for td in tr.find_all('td'):
                                if cont == 0:
                                    mes = td.get_text().split(' ')[0].upper()
                                elif cont == 1:
                                    utm = re_monto_patron.findall(str(td))[0]
                                elif cont == 2:
                                    uta = re_monto_patron.findall(str(td))[0]

                                cont = cont + 1
                            indicadores['MES_UTM'] = mes
                            indicadores['UTM'] = locale.atof(utm)
                            indicadores['UTA'] = locale.atof(uta)

        return indicadores


