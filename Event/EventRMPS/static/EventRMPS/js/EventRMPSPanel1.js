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
        global_version = $('#global_version').text();
    var EventRMPSPanel2 = require('/static/EventRMPS/js/EventRMPSPanel2.js?version=' + global_version);

    var exports = {};
    var timeOut;

    var $Panel1Form1 = $('#EventRMPSPanel1Form1'),
        $Panel1Form1Submit = $('#EventRMPSPanel1Form1Submit'),
        $Panel2Table1Id = $('#EventRMPSPanel2Table1Id');

    var $EventRMPSSaleRegion = $("#sale_region"),
        $EventRMPSTerritory = $("#territory"),
        $EventRMPSCenterId = $("#center_id");
        // $EventRMPSCenterName = $("#center_name");


    function run () {
        init();
        event();
    }

    function init() {
        // $("#DOW").select2({
        //     placeholder: "Default to all if leave empty"
        // });
        //
        // $("#product").select2({
        //     allowClear: false
        // });
        selectionInit();
    }

    function event() {

        $Panel1Form1.submit(function (e) {

            var data = $(this).serialize();
            clearTimeout(timeOut);

            $Panel1Form1Submit.html("Changing...");
            $.get('/Event/EventRMPS/panel1/form1/submit',data,function (res) {
                var status = res['status'],
                    msg = res['msg'];
                if (status === 1){
                    $Panel2Table1Id.bootstrapTable('destroy');
                    var columns = res['columns'];
                    EventRMPSPanel2.Panel2Table1_init(columns);
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

        // $EventRMPSCenterId.parent().find('.select2-selection__rendered').keydown(function (e) {
        //     if (e.which === 13) {
        //         e.preventDefault();
        //
        //         console.log($EventRMPSCenterId.val())
        //     }
        // })

        // refreshProductEvent();
    }

    function selectionInit() {
        refreshSelection('sale_region');
        refreshSelection('territory');
        refreshSelection('center_id');
        refreshSelection('center_name');
    }

    function selectionRefreshEvent() {
        // $EventRMPSGroup.on('change', function () {
        //     $EventRMPSSubGroup.val(null).trigger("change");
        //     $EventRMPSTier.val(null).trigger("change");
        // });
        // $EventRMPSSubGroup.change(function () {
        //     $EventRMPSTier.val(null).trigger("change");
        // });
    }

    function refreshSelection (selectType) {
        var $selectEl = null;

        switch (selectType) {
            case 'sale_region':
                $selectEl = $EventRMPSSaleRegion;
                break;
            case 'territory':
                $selectEl = $EventRMPSTerritory;
                break;
            case 'center_id':
                $selectEl = $EventRMPSCenterId;
                break;
            // case 'center_name':
            //     $selectEl = $EventRMPSCenterName;
            //     break;
        }

        if ($selectEl) {
            $selectEl.select2({
                ajax:{
                    url:'/Event/EventRMPS/panel1/form1/get_selections',
                    data: function (params) {
                        // var formData = new FormData($Panel1Form1[0]);
                        // var result = {};
                        //
                        // result['search'] = params['term'];
                        // result['selectType'] = selectType;
                        // formData.forEach(function (value, key) {
                        //     result[key] = value;
                        // });
                        //
                        // return result

                        return {
                            'search': params['term'],
                            'selectType': selectType,
                            'sale_region': $EventRMPSSaleRegion.val(),
                            'territory': $EventRMPSTerritory.val(),
                            'center_id': $EventRMPSCenterId.val(),
                            // 'center_name': $EventRMPSCenterName.val(),
                        };
                    },
                    processResults: function (data, params) {
                        return {
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
