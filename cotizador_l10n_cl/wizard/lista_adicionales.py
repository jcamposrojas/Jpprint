from odoo import api, fields, models, tools, _

import logging

_logger = logging.getLogger(__name__)


class ListaAdicionales(models.TransientModel):
    _name = 'lista.adicionales'
    _description = 'Lista de adicionales'
    _order = 'id'

    select_id          = fields.Many2one('select.products')
    adicional_id       = fields.Many2one('cotizador.adicional')

    name               = fields.Char('Nombre', related='adicional_id.name')
    add_data           = fields.Boolean('Agrega campo dato?', related='adicional_id.add_data')


    tipo_data          = fields.Selection([('t','Texto'),('s','Selección')])
    texto              = fields.Char('Texto', related='adicional_id.data')
    data_text          = fields.Char('Valor')
    data_selection     = fields.Selection([], string='Selección')

