# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Cuenta Analítica en Sale Order Line",
    "version": "15.0.1.0.1",
    "category": "Sales Management",
    "author": "Vanguardchile",
    "website": "https://www.vanguardchile.cl",
    "license": "AGPL-3",
    "depends": [
        "sale",
        "account",
    ],
    "data": [
        "views/sale_view.xml",
        "data/uom_minute.xml"
    ],
    "installable": True,
    "auto_install": False,
}
