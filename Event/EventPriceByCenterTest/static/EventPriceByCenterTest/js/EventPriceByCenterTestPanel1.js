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
        EventPriceByCenterPanel2 = require('/static/EventPriceByCenter/js/EventPriceByCenterPanel2.js');

    var exports = {};
    var timeOut;

    var $Panel1Form1 = $('#EventPriceByCenterPanel1Form1'),
        $Panel1Form1Submit = $('#EventPriceByCenterPanel1Form1Submit'),
        $Panel2Table1Id = $('#EventPriceByCenterPanel2Table1Id');

    var $EventPriceByCenter_product = $("#product");


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
        refresh_product();
    }

    function event() {

        $Panel1Form1.submit(function (e) {

            var data = $(this).serialize();
            clearTimeout(timeOut);

            $Panel1Form1Submit.html("Changing...");
            $.get('/Event/EventPriceByCenter/panel1/form1/submit',data,function (res) {
                var status = res['status'],
                    msg = res['msg'];
                if (status === 1){
                    $Panel2Table1Id.bootstrapTable('destroy');
                    var columns = res['columns'];
                    EventPriceByCenterPanel2.Panel2Table1_init(columns);
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

    function refresh_product () {
        $EventPriceByCenter_product.select2({
            ajax:{
                url:'/Event/EventPriceByCenter/panel1/form1/get_product',
                data: function (params) {
                  return {
                    'search': params['term'],
                  };
                },
                processResults: function (data, params) {
                    return {
                        results: data['results']
                    };
                }
            }
        });
    }

    exports.run = run;
    exports.refresh_product = refresh_product;

    return exports
});
