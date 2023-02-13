# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import time
from datetime import datetime
import tempfile
import binascii
from datetime import date, datetime
from odoo.exceptions import Warning, UserError
from odoo import models, fields, exceptions, api, _

import logging
_logger = logging.getLogger(__name__)

import io

try:
    import psycopg2
except ImportError:
    _logger.debug("Cannot 'import psycopg2'.")

try:
    import csv
except ImportError:
    _logger.debug("Cannot 'import csv'.")

try:
    import cStringIO
except ImportError:
    _logger.debug("Cannot 'import cStringIO'.")

try:
    import base64
except ImportError:
    _logger.debug("Cannot 'import base64'.")


class ImportTarifa(models.TransientModel):
    _name = "import.tarifa"
    _description = "Importación de Tarifa"

    archivo = fields.Binary(string="Seleccione Archivo .csv")

    
    def import_file(self):
# -----------------------------
            #keys = ['code', 'name', 'user_type_id']
            #RUT	RAZON SOCIAL	NUMERO RESOLUCION	FECHA RESOLUCION	MAIL INTERCAMBIO	URL

        if self.env.context.get('active_id', False):
            producto_id = self.env.context.get('active_id')
            _logger.info(' ACTIVE_ID ')
            _logger.info(producto_id)

            prod = self.env['cotizador.producto'].search([('id','=',producto_id)])
            sustratos = {}
            if prod:
                _logger.info(prod.name)
                for item in prod.producto_sustrato_ids:
                    sustratos[item.sustrato_id.id] = item.sustrato_id.codigo
                    _logger.info(item.sustrato_id.codigo)

            _logger.info(sustratos)


        csv_data = base64.b64decode(self.archivo)
        data_file = io.StringIO(csv_data.decode("latin1"))
        data_file.seek(0)
        csv_reader = csv.reader(data_file, delimiter=';', quotechar="|")
        # Salta header
        #next(csv_reader)

        # Elimina todas las tarifas asociadas al centro de negocio
        self.env['tarifa'].search([('producto_id', '=', producto_id)]).unlink()

        header = True
        sustratos_validos = []
        for row in csv_reader:
            if header == True:
                i = 1
                while i < len(row):
                    if not row[i].strip() in sustratos.values():
                        _logger.info("%s SI esta"%(row[i].strip()))
                        raise UserError("Sustrato '%s' No reconocido!"%(row[i].strip()))

                    key = [k for k, v in sustratos.items() if v == row[i].strip()][0]
                    sustratos_validos.append(key)
                    i = i + 1
                _logger.info('SUSTRATOS VALIDOS')
                _logger.info(sustratos_validos)
                header = False
            else:
                m2 = row[0].strip()
                i = 1
                for sustrato in sustratos_validos:
                    _logger.info("%s %s %s-%s "%(producto_id,sustrato,m2,row[i].strip()))

                    values = {
                        'producto_id' : producto_id,
                        'sustrato_id' : sustrato,
                        'm2'          : m2,
                        'porcentaje'  : row[i].strip(),
                    }
                    self.env['tarifa'].create(values)

                    i = i + 1

