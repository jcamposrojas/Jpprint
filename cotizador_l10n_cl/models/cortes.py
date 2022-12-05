from odoo import api, fields, models, tools, _
from math import floor


class CotizadorCortes(models.Model):
    _name = 'cotizador.cortes'
    _description = 'Cortes de Papel'
    _rec_name = 'codigo'
    _order = 'ancho asc'


    codigo  = fields.Char(string='Descripción', compute='_compute_name', store=True)
    ancho = fields.Integer(string='Ancho de Corte', required=True)

    def _get_default_uom_id(self):
        return self.env.ref('uom.product_uom_millimeter')

    uom_id = fields.Many2one('uom.uom', string='Unidad de Medida', default=_get_default_uom_id)
 
    _sql_constraints = [
        ('ancho_corte_uniq', 'unique (ancho)', 'Los cortes deben ser únicos.'),
        ]

    @api.depends('ancho','uom_id')
    def _compute_name(self):
        for rec in self:
            name = '/'
            if rec.ancho and rec.uom_id:
                name = 'Corte-%s%s' % (rec.ancho,rec.uom_id.name)
            rec.codigo = name

    # ID, ET. AL ANCHO, ANCHO, LARGO(AVANCE)
    def get_max_etiquetas_al_ancho(self, ancho, largo):
        o14 = floor(self.ancho / largo)
        p14 = floor(self.ancho / ancho)
        if o14 > p14:
            return self.id, o14, ancho, largo
        else:
            return self.id, p14, largo, ancho



