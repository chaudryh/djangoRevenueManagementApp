/**
 * Created by caliburn on 17-4-17.
 */
define(function (require) {
    var $ = require('jquery'),
        bootstrap = require('bootstrap'),
        bootstraptable =  require('bootstrap-table'),
        datepicker = require('bootstrap-datepicker'),
        fileinput = require('bootstrap-fileinput'),
        gentelella = require('gentelella'),
        select2 = require('select2'),
        moment = require('moment'),
        PNotify = require('pnotify'),
		PNotify_buttons = require('pnotify-buttons'),
		PNotify_nonblock = require('pnotify-nonblock'),
		PNotify_animate = require('pnotify-animate'),
        // bootstrap table extensions
        // bootstrap_table_export = require('bootstrap-table-export'),
        // tableExport = require('tableExport'),
        x_editable = require('x-editable'),
        flat_json = require('flat-json'),
        multiple_sort = require('multiple-sort'),
        bootstrap_table_editable = require('bootstrap-table-editable'),
        // filter_control = require('filter-control'),
        select2_filter = require('select2-filter');
    var global_version = $('#global_version').text();

    $(function () {
        init();
        event()
    });

    function init() {
        require(['/static/ProductOpt/js/ProductOptPanel2.js?version=' + global_version], function (ProductOptPanel2) {
            ProductOptPanel2.run();
            require(['/static/ProductOpt/js/ProductOptPanel1.js?version=' + global_version], function (ProductOptPanel1) {
                ProductOptPanel1.run()
            });
        });
        require(['/static/ProductOpt/js/ProductOptPanel3.js?version=' + global_version], function (ProductOptPanel3) {
            ProductOptPanel3.run()
        });
    }

    function event() {

    }
});
