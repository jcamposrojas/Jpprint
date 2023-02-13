# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api,fields, models

import logging

_logger = logging.getLogger(__name__)


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    def _compute_price_rule(self, products_qty_partner, date=False, uom_id=False):
        """Recompute price after calling the atomic super method for
        getting proper prices when based on supplier info.
        """
        rule_obj = self.env["product.pricelist.item"]
        result = super()._compute_price_rule(products_qty_partner, date, uom_id)
        # Make sure all rule records are fetched at once at put in cache
        rule_obj.browse(x[1] for x in result.values()).mapped("price_discount")
        context = self.env.context
        for product, qty, _partner in products_qty_partner:
            rule = rule_obj.browse(result[product.id][1])
            if rule.compute_price == "formula" and rule.base == "cotizador" and product.gen_cotizador == 1:
                result[product.id] = (
                    #product.sudo()._get_supplierinfo_pricelist_price(
                    #    rule,
                    #    date=date or context.get("date", fields.Date.today()),
                    #    quantity=qty,
                    #),
                    product.sudo()._get_tarifa_pricelist_price(),
                    #1000,
                    rule.id,
                )
        return result


class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    base = fields.Selection(selection_add=[("cotizador", "Cotización")],
        ondelete={"cotizador": "set default"})

    applied_on = fields.Selection(selection_add=[("4_cotizados", "Productos cotizados")],
        ondelete={"4_cotizados": "set default"})

#    no_supplierinfo_min_quantity = fields.Boolean(
#        string="Ignore Supplier Info Min. Quantity",
#    )
#    filter_supplier_id = fields.Many2one(
#        comodel_name="res.partner",
#        string="Supplier filter",
#        help="Only match prices from the selected supplier",
#    )


    @api.depends('applied_on', 'categ_id', 'product_tmpl_id', 'product_id', 'compute_price', 'fixed_price',
        'pricelist_id', 'percent_price', 'price_discount', 'price_surcharge')
    def _get_pricelist_item_name_price(self):
        super(PricelistItem,self)._get_pricelist_item_name_price()
        for item in self:
            if item.applied_on == '4_cotizados':
                item.name = "Productos Cotizados"

