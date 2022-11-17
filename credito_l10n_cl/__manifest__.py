# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Límite de credito',
    'version' : '15.0.0.11',
    'category' : 'Sales',
    'summary' : '',
    'description': '',
    'author' : 'Vanguardchile',
    'website' : 'https://www.vanguardchile.cl',
    'depends' : ['base',
        'sale',
        'account',
        'sale_management',
        'stock',
        'l10n_cl_edi', # Plazos de pago documentados
        ],
    'data' : [
              'security/ir.model.access.csv',
              'wizard/wizard_credit_limit.xml',
              'views/view_credit_limit.xml',
              'views/account_payment_term_views.xml',
              'edi/customer_credit_limit_mail.xml'
              ],
    'assets': {
        'web.assets_backend': [
            'credito_l10n_cl/static/src/js/account_payment_field.js',
        ],
        'web.assets_qweb': [
            'credito_l10n_cl/static/src/xml/**/*',
        ],
    },

    'installable' : True,
    "license":'OPL-1',
}
