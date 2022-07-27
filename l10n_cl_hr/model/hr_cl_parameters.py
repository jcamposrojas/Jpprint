# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)


class HrPayslipClParameters(models.Model):
    _name = 'hr.payslip.cl.parameters'
    _description = 'Parámetros de Nómina Loc Chile'

    work_entry_type_id = fields.Many2one('hr.work.entry.type', string='Type', required=True, ondelete='cascade',
            index=True, help="The code that can be used in the salary rules")
    name = fields.Char(string='Description', related='work_entry_type_id.name')
    code = fields.Char(string='Code', related='work_entry_type_id.code')

    payslip_id = fields.Many2one('hr.payslip', string='Pay Slip', required=True, ondelete='cascade', index=True)
    sequence = fields.Integer(required=True, index=True, default=10)
    number_of_days = fields.Float(string='Número de días')
    number_of_hours = fields.Float(string='Número de horas')



#@api.depends('work_entry_type_id')
#    def _compute_name(self):
#        for parameters in self:
#            parameters.name = parameters.work_entry_type_id.name

