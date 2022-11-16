# -*- coding: utf-8 -*-
from odoo import fields, models
from num2words import num2words

import logging

_logger = logging.getLogger(__name__)

class Picking(models.Model):
    _inherit = "stock.picking"

    # Datos adicionales a guis de despacho
    rut_transportista = fields.Char('Rut Transportista')
    patente           = fields.Char('Patente')
    rut_chofer        = fields.Char('Rut Chofer')
    nombre_chofer     = fields.Char('Nombre Chofer')

    # Referencia de documentos
    l10n_cl_reference_ids = fields.One2many('l10n_cl.account.invoice.reference', 'stock_picking_id', readonly=False,
            states={'cancel': [('readonly',True)],'done': [('readonly',True)]}, string='Registros Referenciados')

    def _prepare_pdf_values(self):
        rslt = super(Picking, self)._prepare_pdf_values()

        # class tot = float
        amount_f = rslt.get('amounts')['total_amount']
        amount_i = int(round(amount_f, 0))
        amount_total = num2words(amount_i, lang='es').upper()

        result = {
            **rslt,
            **{
                'num_text': amount_total
            }
        }
        return result


