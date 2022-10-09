from odoo import api, fields, models, tools, SUPERUSER_ID, _


class Partner(models.Model):
    _inherit = 'res.partner'

    vendedor_name = fields.Char(string='Vendedor')
