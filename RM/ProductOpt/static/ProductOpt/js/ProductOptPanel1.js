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
        global_version = $('#global_version').text();
    var ProductOptPanel2 = require('/static/ProductOpt/js/ProductOptPanel2.js?version=' + global_version);

    var exports = {};
    var timeOut;

    var $Panel1Form1 = $('#ProductOptPanel1Form1'),
        $Panel1Form1Submit = $('#ProductOptPanel1Form1Submit'),
        $Panel2Table1Id = $('#ProductOptPanel2Table1Id');

    var $date = $("#date");


    function run () {
        init();
        event();
        // PricingTablePanel1.Panel1Table1_init();
    }

    function init() {
        $("#date").datepicker("setDate", new Date());
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
            $.get('/RM/ProductOpt/panel1/form1/submit',data,function (res) {
                var status = res['status'],
                    msg = res['msg'];
                if (status === 1){
                    $Panel2Table1Id.bootstrapTable('destroy');
                    var columns = res['columns'];
                    ProductOptPanel2.Panel2Table1_init($date.val(), columns);
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
