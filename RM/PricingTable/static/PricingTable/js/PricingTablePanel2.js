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
        select2_filter = require('select2-filter'),
        PricingTablePanel1 = require('/static/PricingTable/js/PricingTablePanel1.js');

    var $Panel2Form1 = $('#PricingTablePanel2Form1'),
        $Panel2Form1Submit = $('#PricingTablePanel2Form1Submit'),
        $Panel1Table1Id = $('#PricingTablePanel1Table1Id');

    var $start = $("#start"),
        $end = $("#end");

    var exports = {};
    var timeOut;

    function run () {
        init();
        event();
        // PricingTablePanel1.Panel1Table1_init();
    }

    function init() {
        $("#DOW").select2({
            placeholder: "Default to all if leave empty"
        });

        $("#product").select2({
            allowClear: false
        });
    }

    function event() {

        $Panel2Form1.submit(function (e) {

            var data = $(this).serialize();
            clearTimeout(timeOut);

            $Panel2Form1Submit.html("Changing...");
            $.get('/RM/PricingTable/panel2/form1/submit',data,function (res) {
                var status = res['status'],
                    msg = res['msg'];
                if (status === 1){

                    var columns = res['columns'];

                    $Panel1Table1Id.bootstrapTable('destroy');
                    PricingTablePanel1.Panel1Table1_init($start.val(), $end.val(), columns);
                    $Panel2Form1Submit.html("Refreshed");
                    timeOut = setTimeout(function() {
                        $Panel2Form1Submit.html("Refresh");
                    }, 2000);
                }else {
                    $Panel1Form1Submit.html("Try Again");
                    alert(msg)
                }
            });

            return false
        });
    }

    exports.run = run;

    return exports
});
