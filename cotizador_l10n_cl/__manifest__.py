# -*- coding: utf-8 -*-
{
    'name': 'Cotizador de Productos',
    'version': '15.0.1.0.1',
    'category': 'Sales',
    'summary': 'Cotizador de Productos',
    'description': """
    """,
    'sequence': 1,
    'author': 'JIC',
    'website': 'http://www.vanguardchile.cl',
    'depends': ['base', 'product', 'sale_management', 'purchase','mrp'],
    'data': [
        'wizard/select_products_wizard_view.xml',
        'views/menu_root.xml',
        'views/product_mng_view.xml',
        'views/sustrato_mng_view.xml',
        'views/sale_views.xml',
        'views/purchase_views.xml',
        'views/mrp_routing_views.xml',
        'views/sale_order_view.xml',
        'views/adicional_views.xml',
        'data/ir_sequence_data.xml',
        'data/cotizador_data.xml',
        'data/cotizador_adhesivo.xml',
        'data/cotizador_cilindro.xml',
#        'data/product_calc_sustrato.xml',
#        'data/product_sustrato_rel.xml',
        'security/ir.model.access.csv'
    ],
    'images': [
        'static/description/so_po_multi_product_banner.png',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}
