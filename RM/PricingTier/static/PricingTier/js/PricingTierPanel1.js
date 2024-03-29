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
        PricingTierPanel2 = require('/static/PricingTier/js/PricingTierPanel2.js');

    var exports = {};

    var $Panel1Form1 = $('#PricingTierPanel1Form1'),
        $Panel1Form1Submit = $('#PricingTierPanel1Form1Submit'),
        $Panel2Table1Id = $('#PricingTierPanel2Table1Id');

    var $PricingTier_center_type = $("#center_type"),
        $PricingTier_product = $("#product");


    function run () {
        init();
        event();
        // PricingTablePanel1.Panel1Table1_init();
    }

    function init() {
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


            $Panel1Form1Submit.html("Changing...");
            $.get('/RM/PricingTier/panel1/form1/submit',data,function (res) {
                var status = res['status'],
                    msg = res['msg'];
                if (status === 1){
                    $Panel2Table1Id.bootstrapTable('destroy');
                    var columns = res['columns'];
                    PricingTierPanel2.Panel2Table1_init($PricingTier_center_type.val(), $PricingTier_product.val(), columns);
                    $Panel1Form1Submit.html("Refreshed");
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
