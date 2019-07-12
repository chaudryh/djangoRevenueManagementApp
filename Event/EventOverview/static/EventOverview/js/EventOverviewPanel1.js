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
        select2_filter = require('select2-filter'),
        EventOverviewPanel2 = require('/static/EventOverview/js/EventOverviewPanel2.js');

    var exports = {};
    var timeOut;

    var $Panel1Form1 = $('#EventOverviewPanel1Form1'),
        $Panel1Form1Submit = $('#EventOverviewPanel1Form1Submit'),
        $Panel2Table1Id = $('#EventOverviewPanel2Table1Id');

    var $start = $("#start"),
        $end = $("#end"),
        $eff_start = $('#eff_start'),
        $eff_end = $('#eff_end');


    function run () {
        init();
        event();
        // PricingTablePanel1.Panel1Table1_init();
    }

    function init() {
        // var now = moment();
        // var now_30days = moment().subtract(30, 'days');
        // $start.datepicker("setDate", now_30days.format("YYYY-MM-DD"));
        // $end.datepicker("setDate", now.format("YYYY-MM-DD"));
        // $("#DOW").select2({
        //     placeholder: "Default to all if leave empty"
        // });
        //
        // $("#product").select2({
        //     allowClear: false
        // });
    }

    function event() {

        $Panel1Form1.submit(function (e) {

            var data = $(this).serialize();
            clearTimeout(timeOut);

            $Panel1Form1Submit.html("Changing...");
            $.get('/Event/EventOverview/panel1/form1/submit',data,function (res) {
                var status = res['status'],
                    msg = res['msg'];
                if (status === 1){
                    $Panel2Table1Id.bootstrapTable('destroy');
                    var columns = res['columns'];
                    EventOverviewPanel2.Panel2Table1_init(
                        $start.val(), $end.val(),
                        $eff_start.val(), $eff_end.val(),
                        columns
                    );
                    $Panel1Form1Submit.html("Refreshed");
                    timeOut = setTimeout(function() {
                        $Panel1Form1Submit.html("Submit");
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
