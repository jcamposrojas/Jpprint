odoo.define('cotizador_l10n_cl.widget_tarifa', function (require) {
"use strict";

var AbstractField = require('web.AbstractField');
var core = require('web.core');
var field_registry = require('web.field_registry');
var field_utils = require('web.field_utils');

var QWeb = core.qweb;
var _t = core._t;

var ShowTarifaLineWidget = AbstractField.extend({
    supportedFieldTypes: ['char'],

    /**
     * @private
     * @override
     */
    _render: function() {
        var self = this;
        //var info = JSON.parse(this.value);
        var info = this.value;
	alert(info);
        if (!info) {
            this.$el.html('');
            return;
        }
        _.each(info.content, function (k, v){
            k.index = v;
            k.amount = field_utils.format.float(k.amount, {digits: k.digits});

		/*
	    **
            if (k.payment_date){
                k.payment_date = field_utils.format.date(field_utils.parse.date(k.payment_date, {}, {isUTC: true}));
            }
	    */
        });
        this.$el.html(QWeb.render('ShowTarifaWidget', {
            data: info,
		/*
            data: info.data,
            lines: info.content,
            param: info.param,
	    count_parametros: info.count_parametros,
	    aisa: info.aisa,
	    */
        }));
    },

});

field_registry.add('widget_tarifa', ShowTarifaLineWidget);

return {
    ShowTarifaLineWidget: ShowTarifaLineWidget
};

});
