# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)


class HrPayslipInputType(models.Model):
    _inherit = 'hr.payslip.input.type'

    show_input = fields.Boolean('Agrega input en Nómina', default=False)
    invisible_show_input = fields.Boolean(compute='_compute_invisible_show_input')

#    @api.depends('show_input')
    def _compute_invisible_show_input(self):
        attachment_types = self._get_attachment_types()
        attachment_type_ids = [f.id for f in attachment_types.values()]
        for input_type in self:
            _logger.info(' CCCC ')
            _logger.info(attachment_types)
            _logger.info(attachment_type_ids)
            if input_type.id in attachment_type_ids:
                input_type.invisible_show_input = True
            else:
                input_type.invisible_show_input = False

    # Analogo al existente en hr_payslip
    @api.model
    def _get_attachment_types(self):
        return {
            'attachment': self.env.ref('hr_payroll.input_attachment_salary'),
            'assignment': self.env.ref('hr_payroll.input_assignment_salary'),
            'child_support': self.env.ref('hr_payroll.input_child_support'),
        }

