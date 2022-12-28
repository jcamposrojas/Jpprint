from odoo import api, fields, models, tools, _

class TintaBlancaLines(models.Model):
    _name = 'tinta_blanca_lines'
    _description = 'Tinta Blanca Jetrion Lineas'

    producto_id = fields.Many2one("cotizador.producto", string="Producto")
    porcentaje  = fields.Integer(string='Porcentaje %')
    valor       = fields.Float(string='Valor', compute='_compute_valor')
    tblanca_costo_unitario_consumo = fields.Float(string='Costo unitario consumo',
                                     related='producto_id.tblanca_costo_unitario_consumo')
    name        = fields.Char(compute='_compute_name')

    _sql_constraints = [
           ('porcentaje_constraint',
            'CHECK(porcentaje >= 0 AND porcentaje <= 100)',
            'Porcentaje debe ser >= 0 y <= 100'),
        ]

    @api.depends('porcentaje','tblanca_costo_unitario_consumo')
    def _compute_valor(self):
        for rec in self:
            if rec.porcentaje and rec.tblanca_costo_unitario_consumo:
                rec.valor = rec.tblanca_costo_unitario_consumo * (rec.porcentaje/100.0)
            else:
                rec.valor = 0

    @api.depends('porcentaje')
    def _compute_name(self):
        for rec in self:
            rec.name = "%s %%" % (rec.porcentaje)
#        res = []
#        for record in self:
#            res.append((record.id,"%s %%" % (record.porcentaje)))
#        return res
