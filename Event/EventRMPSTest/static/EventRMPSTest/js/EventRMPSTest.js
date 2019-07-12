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
        bootstrap_table_export = require('bootstrap-table-export'),
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
        require(['/static/EventRMPSTest/js/EventRMPSTestPanel2.js?version=' + global_version], function (EventRMPSTestPanel2) {
            EventRMPSTestPanel2.run();
            require(['/static/EventRMPSTest/js/EventRMPSTestPanel1.js?version=' + global_version], function (EventRMPSTestPanel1) {
                EventRMPSTestPanel1.run();
            });
        });
        require(['/static/EventRMPSTest/js/EventRMPSTestPanel3.js?version=' + global_version], function (EventRMPSTestPanel3) {
            EventRMPSTestPanel3.run();
        });
    }

    function event() {

    }
});
