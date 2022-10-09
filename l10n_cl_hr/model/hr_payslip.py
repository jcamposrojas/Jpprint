from pytz import timezone
from datetime import date, datetime, time, timedelta

from odoo import api, fields, models, tools, _, Command
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.addons.hr_payroll.models.browsable_object import BrowsableObject

import logging
_logger = logging.getLogger(__name__)

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    _description = 'Pay Slip'
    
    indicadores_id = fields.Many2one('hr.indicadores', string='Indicadores',
        readonly=True, states={'draft': [('readonly', False)]},
        help='Defines Previred Forecast Indicators')
    movimientos_personal = fields.Selection([('0', 'Sin Movimiento en el Mes'),
     ('1', 'Contratación a plazo indefinido'),
     ('2', 'Retiro'),
     ('3', 'Subsidios (L Médicas)'),
     ('4', 'Permiso Sin Goce de Sueldos'),
     ('5', 'Incorporación en el Lugar de Trabajo'),
     ('6', 'Accidentes del Trabajo'),
     ('7', 'Contratación a plazo fijo'),
     ('8', 'Cambio Contrato plazo fijo a plazo indefinido'),
     ('11', 'Otros Movimientos (Ausentismos)'),
     ('12', 'Reliquidación, Premio, Bono')     
     ], string='Código Movimiento', default="0")

    date_start_mp = fields.Date('Fecha Inicio MP',  help="Fecha de inicio del movimiento de personal")
    date_end_mp = fields.Date('Fecha Fin MP',  help="Fecha del fin del movimiento de personal")

    #compute='_compute_parameters', store=True, readonly=True, copy=True,
    parameters_ids = fields.One2many('hr.payslip.cl.parameters', 'payslip_id', string='Parámetros Nómina CL',
            store=True, copy=True, states={'draft': [('readonly', False)], 'verify': [('readonly', False)]})


    #@api.onchange('employee_id', 'contract_id', 'struct_id', 'date_from', 'date_to')
    #@api.onchange('date_from', 'date_to', 'struct_id')
    def _compute_fest(self):
        fest_entry = self.env['hr.work.entry.type'].search([('code', '=', 'FEST')])
        for payslip in self:
            values = []

            #payslip.parameters_ids = [(5, 0, 0)]

            # Primer/ultimo dia del mes anterior. Semana corrida
            date_to   = payslip.date_to.replace(day=1) - timedelta(days=1)
            date_from = date_to.replace(day=1)

            if date_from and date_to and date_from <= date_to:
                date_now = date_from

                count_festivos = 0
                festivos = self.env['resource.calendar.leaves'].search([
                            ('work_entry_type_id.code','=','FEST'),
                            ('company_id', '=', self.env.company.id),
                        ])
                while date_now <= date_to:
                    if int(date_now.strftime("%w")) == 0:
                        count_festivos = count_festivos + 1
                    else:
                        if festivos:
                            for fest in festivos:
                                # dia festivo
                                if date_now >= fest.date_from.date() and date_now <= fest.date_to.date():
                                    count_festivos = count_festivos + 1
                    date_now = (date_now + timedelta(1))

                #values.append({
                values = {
                    'sequence': 10,
                    'work_entry_type_id': fest_entry.id,
                    'number_of_days': count_festivos,
                    'number_of_hours': 0,
                    #'name': fest_entry.name,
                    'name': 'Festivos Mes Anterior',
                    'payslip_id'    : self.id,
                }
 
                for record in payslip.parameters_ids:
                    if record.work_entry_type_id.id == fest_entry.id:
                        self.write({'parameters_ids': [(2,record.id)]})


                payslip.parameters_ids = [(0,0,values)]
            #payslip.parameters_ids.append(values)
            #payslip.update({'parameters_ids':[(0,0,values)]})


    @api.model
    def create(self, vals):
        #JCR revisar. 
        if 'parameters_ids' in self.env.context:
            vals['parameters_ids'] = self.env.context.get('parameters_ids')
        if 'indicadores_id' in self.env.context:
            vals['indicadores_id'] = self.env.context.get('indicadores_id')
        if 'movimientos_personal' in self.env.context:
            vals['movimientos_personal'] = self.env.context.get('movimientos_personal')
        return super(HrPayslip, self).create(vals)

    @api.model
    def _get_worked_day_lines(self, domain=None, check_out_of_contract=True):
        res = super(HrPayslip, self)._get_worked_day_lines(domain, check_out_of_contract)
        temp = 0 
        dias = 0
        attendances = {}
        leaves = []

        for line in res:
            entry = self.env['hr.work.entry.type'].search([('id', '=', line.get('work_entry_type_id'))])

            if entry.code == 'WORK100':
            #if line.get('work_entry_type_id.code') == 'WORK100':
                attendances = line
            else:
                leaves.append(line)
        for leave in leaves:
            temp += leave.get('number_of_days') or 0

        #Dias laborados reales para calcular la semana corrida
        effective = attendances.copy()
        entry_effective = self.env['hr.work.entry.type'].search([('code', '=', 'EFF100')])
        effective.update({
            'name': _("Dias de trabajo efectivos"),
            'sequence': 2,
            #'code': 'EFF100',
            'payslip_id'    : self.id,
            'work_entry_type_id': entry_effective.id,
        })

        # En el caso de que se trabajen menos de 5 días tomaremos los dias trabajados en los demás casos 30 días - las faltas
        # Estos casos siempre se podrán modificar manualmente directamente en la nomina.
        # Originalmente este dato se toma dependiendo de los dias del mes y no de 30 dias
        # TODO debemos saltar las vacaciones, es decir, las vacaciones no descuentan dias de trabajo. 
        if (effective.get('number_of_days') or 0) < 5:
            dias = effective.get('number_of_days')
        else:
            dias = 30 - temp
        attendances['number_of_days'] = dias
        res = []
        res.append(attendances)

        #self.update({'parameters_ids':  [(5,0,0), (0,0,effective), (0,0,festivos)]})
        #self.update({'parameters_ids':  [(5,0,0), (0,0,effective)]})
        #self.update({'parameters_ids':  [(0,0,effeemp_asses_ques_rev_idsctive)]})
        for record in self.parameters_ids:
            if record.work_entry_type_id.id == effective.get('work_entry_type_id'):
                self.write({'parameters_ids': [(2,record.id)]})

        self.parameters_ids = [(0,0,effective)]

        self._compute_fest()

        res.extend(leaves)
        return res


    @api.model
    def _get_localdict(self):
        self.ensure_one()

        localdict = super(HrPayslip, self)._get_localdict()

        parameters = {line.code: line for line in self.parameters_ids if line.code}

        employee = self.employee_id

        res_localdict = {
            **localdict,
            **{
                'parameters': BrowsableObject(employee.id, parameters, self.env),
            }
        }
        return res_localdict

    @api.depends('employee_id', 'contract_id', 'struct_id', 'date_from', 'date_to', 'struct_id')
    def _compute_input_line_ids(self):

        super()._compute_input_line_ids()

        types_to_show  = self.env['hr.payslip.input.type'].search([('show_input','=',True)])
        for slip in self:
            input_line_vals = [(5,0,0)]

            for type_to_show in types_to_show:
                values = {
                        'name': type_to_show.name,
                        'amount': 0,
                        'input_type_id': type_to_show.id,
                    }
                input_line_vals += [(0,0,values)]
            slip.update({'input_line_ids': input_line_vals})

