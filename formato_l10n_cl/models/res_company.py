# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    l10n_cl_info_sucursales = fields.Html('Información Sucursales', default="")

