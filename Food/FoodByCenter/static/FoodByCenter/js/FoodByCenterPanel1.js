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
    var FoodByCenterPanel2 = require('/static/FoodByCenter/js/FoodByCenterPanel2.js?version=' + global_version),
        $Price = $('#price');


    var exports = {};
    var timeOut;

    var $Panel1Form1 = $('#FoodByCenterPanel1Form1'),
        $Panel1Form1Submit = $('#FoodByCenterPanel1Form1Submit'),
        $Panel2Table1Id = $('#FoodByCenterPanel2Table1Id');

    var $Start = $("#start"),
        $FoodDistrict = $("#district"),
        $FoodRegion = $("#region"),
        $FoodCenter = $("#center_id"),
        $FoodMenuId = $("#menu_id"),
        $FoodCategory = $("#category");


    function run () {
        init();
        event();
    }

    function init() {
        $Start.datepicker("setDate", moment()._d);
        selectionInit()
    }

    function event() {

        $Panel1Form1.submit(function (e) {

            clearTimeout(timeOut);

            var data = $(this).serializeArray();
            if ($Price.val()) {
                var rows = $Panel2Table1Id.bootstrapTable('getAllSelections');
                $.each(rows, function (index, row) {
                    data.push({'name': 'category_products', 'value': row['category'] + '---' + row['product_num']})
                });
            }

            $Panel1Form1Submit.html("Changing...");
            $.get('/Food/FoodByCenter/panel1/form1/submit',data,function (res) {
                var status = res['status'],
                    msg = res['msg'];
                if (status === 1){
                    $Panel2Table1Id.bootstrapTable('destroy');
                    var columns = res['columns'];
                    FoodByCenterPanel2.Panel2Table1_init(columns);
                    $Panel1Form1Submit.html("Refreshed");

                    if($Price.val()){
                        alert("RMS is updating your price changes. Price changes for all centers may take up to 15 mins. " +
                            "Subsequently the changes will be displayed in the 'Change Report'.")
                    }

                    $Price.val('');
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

    function selectionInit() {
        refreshSelection('district');
        refreshSelection('region');
        refreshSelection('center_id');
        refreshSelection('menu_id');
        refreshSelection('category');
    }

    function refreshSelection (selectType) {
        var $selectEl = null;

        switch (selectType) {
            case 'district':
                $selectEl = $FoodDistrict;
                break;
            case 'region':
                $selectEl = $FoodRegion;
                break;
            case 'center_id':
                $selectEl = $FoodCenter;
                break;
            case 'menu_id':
                $selectEl = $FoodMenuId;
                break;
            case 'category':
                $selectEl = $FoodCategory;
                break;
        }

        if ($selectEl) {
            $selectEl.select2({
                ajax:{
                    url:'/Food/FoodByCenter/panel1/form1/get_selections',
                    data: function (params) {
                        return {
                            'search': params['term'],
                            'selectType': selectType,
                            'district': $FoodDistrict.val(),
                            'region': $FoodRegion.val(),
                            'center_id': $FoodCenter.val(),
                            'menu_id': $FoodMenuId.val(),
                            'category': $FoodCategory.val(),
                            'start': $Start.val()
                        };
                    },
                    processResults: function (data, params) {
                        return {
                            //result is a combination of center name and ID
                            results: data['results']
                        };
                    }
                },
                templateSelection: function (data) {

                    if (selectType === 'center_id') {
                        return data.id;
                    } else {
                        return data.text;
                    }
                }
            });
        }
    }

    exports.run = run;

    return exports
});
