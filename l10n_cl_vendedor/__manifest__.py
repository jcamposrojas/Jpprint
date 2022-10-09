{
    'name': 'Add Campo Vendedor',
    'version': '15.0.2',
    'category': '',
    'sequence': 6,
    'license': 'LGPL-3',
    'summary': '',
    'description': """
    Oculta campo user_id y agrega vendedor_name
        """,
    'author': "Vanguardchile",
    'website': 'www.vanguardchile.cl',
    'depends': ['base','sale','purchase'],
    'data': [
        'views/res_partner_views.xml',
    ],
    'installable': True,
}
