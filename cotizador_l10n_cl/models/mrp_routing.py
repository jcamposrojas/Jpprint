# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _, tools


class CotizadorMrpRoutingWorkcenter(models.Model):
    _name = 'mrp.routing.workcenter.tmp'
    _order = 'sequence, id'

    company_id       = fields.Many2one('res.company', default=lambda self: self.env.company)
    cost_currency_id = fields.Many2one('res.currency', readonly=True, related='company_id.currency_id')

    name                   = fields.Char('Operation', required=True)
    #active = fields.Boolean(default=True)
    #workcenter_id = fields.Many2one('mrp.workcenter', 'Work Center', required=True, check_company=True)
    workcenter_id          = fields.Many2one('mrp.workcenter', 'Work Center', required=True)
    sequence               = fields.Integer( 'Sequence', default=100,
                             help="Gives the sequence order when displaying a list of routing Work Centers.")
    cotizador_producto_id  = fields.Many2one( 'cotizador.producto', string='Producto',
                             index=True, ondelete='cascade', required=True, help="")
#    company_id = fields.Many2one('res.company', 'Company', related='bom_id.company_id')
    worksheet_type         = fields.Selection([ ('pdf', 'PDF'), ('google_slide', 'Google Slide'), ('text', 'Text')],
                             string="Work Sheet", default="text",
                             help="Defines if you want to use a PDF or a Google Slide as work sheet.")
    note                   = fields.Html('Description', help="Text worksheet description")
    worksheet              = fields.Binary('PDF')
    worksheet_google_slide = fields.Char('Google Slide', help="Paste the url of your Google Slide. Make sure the access to the document is public.")
    time_mode              = fields.Selection([('auto', 'Compute based on tracked time'),
        ('manual', 'Set duration manually')], string='Duration Computation', default='manual')
    time_mode_batch        = fields.Integer('Based on', default=10)

    incluye_hh             = fields.Boolean(string='Incluye HH', default=False)
    hh_type                = fields.Selection([ ('m', 'Por Metro'), ('t', 'Por Tiempo')],
                             default='m', string='Cálculo de HH')
    costs_hour             = fields.Float(string='Costo Hora', related='workcenter_id.costs_hour')
    costs_min              = fields.Float(string='Costo Min', compute='_compute_costs_min')
    metros_x_min           = fields.Float(string='Metros por minuto', default=0)
    seg_x_etiqueta         = fields.Integer(string='Segundos por etiqueta', default=0)

    def _get_default_uom_id(self):
        return self.env.ref('cotizador_l10n_cl.product_uom_minute')

    uom_id_de_consumo      = fields.Many2one('uom.uom', string='Unidad de Medida', default=_get_default_uom_id)


    @api.depends('costs_hour')
    def _compute_costs_min(self):
        for rec in self:
            if rec.costs_hour and rec.costs_hour > 0:
                rec.costs_min = rec.costs_hour / 60
            else:
                rec.costs_min = 0.0

#    time_computed_on = fields.Char('Computed on last', compute='_compute_time_computed_on')
#    time_cycle_manual = fields.Float(
#        'Manual Duration', default=60,
#        help="Time in minutes:"
#        "- In manual mode, time used"
#        "- In automatic mode, supposed first time when there aren't any work orders yet")
#    time_cycle = fields.Float('Duration', compute="_compute_time_cycle")
#    workorder_count = fields.Integer("# Work Orders", compute="_compute_workorder_count")
#    workorder_ids = fields.One2many('mrp.workorder', 'operation_id', string="Work Orders")
#    possible_bom_product_template_attribute_value_ids = fields.Many2many(related='bom_id.possible_product_template_attribute_value_ids')
#    bom_product_template_attribute_value_ids = fields.Many2many(
#        'product.template.attribute.value', string="Apply on Variants", ondelete='restrict',
#        domain="[('id', 'in', possible_bom_product_template_attribute_value_ids)]",
#        help="BOM Product Variants needed to apply this line.")

#    @api.depends('time_mode', 'time_mode_batch')
#    def _compute_time_computed_on(self):
#        for operation in self:
#            operation.time_computed_on = _('%i work orders') % operation.time_mode_batch if operation.time_mode != 'manual' else False
