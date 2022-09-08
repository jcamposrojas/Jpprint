{
    'name': 'Chilean Payroll & Human Resources',
    'author': 'Vanguardchile',
    'website': 'http://www.vanguardchile.cl',
    'license': 'AGPL-3',
    'depends': [
            'hr_payroll',
            'hr_payroll_account',
            'hr_holidays'
        ],
    'external_dependencies': {
        'python': [
                'num2words'
                ]
        },
    'contributors': [
        "Vanuardchile",
        "KONOS",
    ],
    'license': 'AGPL-3',
    'version': '15.0.1.0.3',
    'description': """
Chilean Payroll & Human Resources.
==================================
    -Payroll configuration for Chile localization.
    Basado en versión KONOS
  """,
    'category': 'Localization/Chile',
    'data': [
        'views/menu_root.xml',
        'views/hr_indicadores_previsionales_view.xml',
        'views/hr_salary_rule_view.xml',
        'views/hr_contract_view.xml',
        'views/hr_employee.xml',
        'views/hr_payslip_view.xml',
        'views/hr_afp_view.xml',
        'views/hr_payslip_run_view.xml',
        'views/report_payslip.xml',
        'views/report_hrsalarybymonth.xml',
        'views/hr_salary_books.xml',
        'views/hr_holiday_views.xml',
        'views/wizard_export_csv_previred_view.xml',
        'views/hr_payslip_input_type.xml',
        'data/hr_work_entry.xml',
        'data/hr_salary_rule_category.xml',
        'data/hr_centros_costos.xml',
        'data/l10n_cl_hr_indicadores.xml',
        'data/l10n_cl_hr_isapre.xml',
        'data/l10n_cl_hr_afp.xml',
        'data/l10n_cl_hr_mutual.xml',
        'data/l10n_cl_hr_apv.xml',
        'data/hr_type_employee.xml',
        'data/resource_calendar_attendance.xml',
        'data/hr_holidays_status.xml',
        'data/hr_contract_type.xml',
        'data/l10n_cl_hr_ccaf.xml',
        'data/account_journal.xml',
        'data/partner.xml',
        'data/l10n_cl_hr_payroll_data.xml',
        'security/ir.model.access.csv',
    ],
    'demo': ['demo/l10n_cl_hr_payroll_demo.xml'],
    'installable': True,
    'application': True,
    'auto_install': False
}
