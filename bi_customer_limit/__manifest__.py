# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Límite de credito',
    'version' : '15.0.0.6',
    'category' : 'Sales',
    'summary' : '',
    'description': '',
    'author' : 'Vanguardchile',
    'website' : 'https://www.vanguardchile.cl',
    'price': 10,
    'currency': "CLP",
    'depends' : ['base', 'sale', 'account','sale_management', 'stock'],
    'data' : [
              'security/ir.model.access.csv',
              'wizard/wizard_credit_limit.xml',
              'views/view_credit_limit.xml',
              'edi/customer_credit_limit_mail.xml'
              ],
    # JCR. causa problema con la visualización de pagos en la factura
#    'assets': {
#        'web.assets_backend': [
#            'bi_customer_limit/static/src/js/account_payment_field.js',
#        ],
#        'web.assets_qweb': [
#            'bi_customer_limit/static/src/xml/**/*',
#        ],
#    },

    'installable' : True,
    "license":'OPL-1',
}
