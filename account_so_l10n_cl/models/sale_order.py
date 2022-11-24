# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    analytic_account_id = fields.Many2one(comodel_name='account.analytic.account',string='Cta. Analítica')

    #@api.multi
    def _prepare_invoice_line(self, **optional_values):
        self.ensure_one()
        res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        if self.analytic_account_id:
            res.update({
                'analytic_account_id': self.analytic_account_id.id,
                })
        return res
