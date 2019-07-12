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
        CenterTestPanel2 = require('/static/CenterTest/js/CenterTestPanel2.js');


    var exports = {},
        table_params;
    var timeOut;

    var
        $CenterDistrict = $("#district"),
        $CenterRegion = $("#region");

    var $Panel1Form1 = $('#CenterTestPanel1Form1'),
        $Panel1Form1Submit = $('#CenterTestPanel1FormSubmit'),
        $Panel1Table1Id = $('#CenterTestPanel2Table1Id');

    function run () {
        init();
        event()
    }

    function init() {
        selectionInit()

    }

    function event() {


        $Panel1Form1.submit(function (e) {

            var data = $(this).serialize();
            clearTimeout(timeOut);

            $Panel1Form1Submit.html("Changing...");
            $.get('/RM/CenterTest/panel1/form1/submit',data,function (res) {
                var status = res['status'],
                    msg = res['msg'];
                if (status === 1){

                    var columns = res['columns'];

                    $Panel1Table1Id.bootstrapTable('destroy');
                    CenterTestPanel2.Panel2Table1_init(columns);
                    $Panel1Form1Submit.html("Refreshed");
                    timeOut = setTimeout(function() {
                        $Panel1Form1Submit.html("Refresh");
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
    }

    function refreshSelection (selectType) {
        var $selectEl = null;

        switch (selectType) {
            case 'district':
                $selectEl = $CenterDistrict;
                break;
            case 'region':
                $selectEl = $CenterRegion;
                break;

        }

        if ($selectEl) {
            $selectEl.select2({
                ajax:{
                    url:'/RM/CenterTest/panel1/form1/get_selections',
                    data: function (params) {
                        return {
                            'search': params['term'],
                            'selectType': selectType,
                            'district': $CenterDistrict.val(),
                            'region': $CenterRegion.val(),

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
