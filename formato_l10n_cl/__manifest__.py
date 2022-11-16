{
    'name': 'Adecuaciones. Formato Factura',
    'version': '15.0.9',
    'category': '',
    'sequence': 6,
    'license': 'LGPL-3',
    'summary': '',
    'description': """
    Versión para Cliente DICOMAC

    UPDATE:
    20220930 Agrega Número de OC a Guia
    20221002 Agrega Referencia cruzadas en Guia de salida
    20221008 Agrega cedible
    20221012 Reemplaza nombre producto por etiqueta en factura
        """,
    'author': "Vanguardchile",
    'website': 'www.vanguardchile.cl',
    'depends': ['account', 'l10n_cl','l10n_cl_edi','l10n_cl_edi_stock'],
    'data': [
        'views/report_invoice.xml',
        'views/res_config_settings_view.xml',
        'views/stock_picking_view.xml',
        'views/report_delivery_guide.xml',
    ],
    'installable': True,
}
