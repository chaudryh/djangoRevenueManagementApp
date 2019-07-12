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
        BundlePanel2 = require('/static/Bundle/js/BundlePanel2.js');

    var exports = {};

    var $Panel1Form1 = $('#BundlePanel1Form1'),
        $Panel1Form1Submit = $('#BundlePanel1Form1Submit'),
        $Panel2Table1Id = $('#BundlePanel2Table1Id');

    var $price_type = $("#price_type"),
        $date = $("#date"),
        $tiers = $('#tiers');


    function run () {
        init();
        event();
        // PricingTablePanel1.Panel1Table1_init();
    }

    function init() {
        // $("#date").datepicker("setDate", new Date());
        $tiers.select2({
            placeholder: "Default To All",
            allowClear: true
        });
        //
        // $("#product").select2({
        //     allowClear: false
        // });
        refresh_Bundle_tiers()
    }
    //Not currently being used in Promo page since first panel doesn't exit'
    function event() {

        $Panel1Form1.submit(function (e) {

            var data = $(this).serializeArray(),
                categories = $Panel2Table1Id.bootstrapTable('getAllSelections'),
                categories_list = [];

            categories.forEach(function (category) {
                categories_list.push(category['category_id'])
            });
            data.push({name: 'categories', value: categories_list});
            data.push({name: 'date', value: $date.val()});
            data.push({name: 'price_type', value: $price_type.val()});

            $Panel1Form1Submit.html("Changing...");
            $.get('/RM/Bundle/panel1/form1/submit',data,function (res) {
                var status = res['status'],
                    msg = res['msg'];
                if (status === 1){
                    $Panel2Table1Id.bootstrapTable('refresh');
                    var columns = res['columns'];
                    $Panel1Form1Submit.html("Submitted");
                }else {
                    $Panel1Form1Submit.html("Try Again");
                    alert(msg)
                }
            });

            return false
        });

    }

    function refresh_Bundle_tiers () {
        // $Bundle_menu.select2({
        //     ajax:{
        //         url:'/RM/Bundle/panel1/form1/Bundle_menu',
        //         data: function (params) {
        //           return {
        //             // 'start': start_global,
        //             // 'end': end_global
        //           };
        //         },
        //         processResults: function (data, params) {
        //             return {
        //                 results: data['results']
        //             };
        //         }
        //     }
        // });
    }

    function clear_form () {
        // clear form 1
        // $Panel2Form1Start.val('');
        // $Panel2Form1End.val('');
        // $Panel2Form1DOW.val(null).trigger('change');
        // // clear form 1a
    }

    exports.run = run;
    exports.refresh_Bundle_tiers = refresh_Bundle_tiers;

    return exports
});
