# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    l10n_cl_info_sucursales = fields.Html('Información Sucursales', related='company_id.l10n_cl_info_sucursales', readonly=False)
