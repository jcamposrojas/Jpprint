# -*- coding: utf-8 -*-
{
    'name': 'Cotizador de Productos',
    'version': '15.0.1.11',
    'category': 'Sales',
    'summary': 'Cotizador de Productos',
    'description': """
    """,
    'sequence': 1,
    'author': 'JIC',
    'website': 'http://www.vanguardchile.cl',
    'depends': ['base', 'product', 'sale_management', 'purchase', 'stock', 'mrp'],
    'data': [
        'wizard/select_products_wizard_view.xml',
        'views/menu_root.xml',
        'views/product_mng_view.xml',
        'views/sustrato_mng_view.xml',
        'views/sale_views.xml',
        'views/mrp_routing_views.xml',
#        'views/sale_order_view.xml',
        'views/troquel_views.xml',
#        'views/rendimiento_adicional_view.xml',
        'views/product_template_view.xml',
        'views/consumo.xml',
        'views/buje.xml',
        'data/ir_sequence_data.xml',
        'data/sustratos.xml',
        'data/productos.xml',
        'data/producto_sustratos.xml',
        'data/cotizador_adhesivo.xml',
        'data/troquel.xml',
        'data/buje.xml',
        'data/aisa.xml',
        'wizard/insumo.xml',
        'security/ir.model.access.csv'
    ],
    'images': [
        'static/description/so_po_multi_product_banner.png',
    ],


    'assets': {
        'web.assets_backend': [
            'cotizador_l10n_cl/static/src/js/radio_image_aisa.js',
            'cotizador_l10n_cl/static/src/js/widget_parametros.js',
        ],
        'web.assets_qweb': [
            'cotizador_l10n_cl/static/src/xml/**/*',
        ],
    },


    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}
