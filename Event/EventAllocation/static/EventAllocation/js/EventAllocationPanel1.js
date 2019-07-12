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
        EventAllocationPanel2 = require('/static/EventAllocation/js/EventAllocationPanel2.js');

    var exports = {};
    var timeOut;

    var $Panel1Form1 = $('#EventAllocationPanel1Form1'),
        $Panel1Form1Submit = $('#EventAllocationPanel1Form1Submit'),
        $Panel2Table1Id = $('#EventAllocationPanel2Table1Id');

    var $EventAllocationGroup = $("#group"),
        $EventAllocationSubGroup = $("#subGroup"),
        $EventAllocationProduct = $("#product"),
        $EventAllocationTier = $("#tier");

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
        refreshAllocationInit();
    }

    function event() {

        $Panel1Form1.submit(function (e) {

            var data = $(this).serialize();
            clearTimeout(timeOut);

            $Panel1Form1Submit.html("Changing...");
            $.get('/Event/EventAllocation/panel1/form1/submit',data,function (res) {
                var status = res['status'],
                    msg = res['msg'];
                if (status === 1){
                    $Panel2Table1Id.bootstrapTable('destroy');
                    var columns = res['columns'];
                    EventAllocationPanel2.Panel2Table1_init(columns);
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

        refreshAllocationEvent();
    }

    function refreshAllocationInit() {
            refreshAllocation('group');
            refreshAllocation('subGroup');
            refreshAllocation('product');
            refreshAllocation('tier');
    }

    function refreshAllocationEvent() {
        $EventAllocationGroup.on('change', function () {
            $EventAllocationSubGroup.val(null).trigger("change");
            $EventAllocationProduct.val(null).trigger("change");
            $EventAllocationTier.val(null).trigger("change");
        });
        $EventAllocationSubGroup.change(function () {
            $EventAllocationProduct.val(null).trigger("change");
            $EventAllocationTier.val(null).trigger("change");
        });
        $EventAllocationProduct.change(function () {
            $EventAllocationTier.val(null).trigger("change");
        })
    }

    function refreshAllocation (selectType) {
        var $selectEl = null;

        switch (selectType) {
            case 'group':
                $selectEl = $EventAllocationGroup;
                break;
            case 'subGroup':
                $selectEl = $EventAllocationSubGroup;
                break;
            case 'product':
                $selectEl = $EventAllocationProduct;
                break;
            case 'tier':
                $selectEl = $EventAllocationTier;
                break;
        }

        if ($selectEl) {
            $selectEl.select2({
                ajax:{
                    url:'/Event/EventAllocation/panel1/form1/get_allocation',
                    data: function (params) {
                        return {
                            'search': params['term'],
                            'selectType': selectType,
                            'group': $EventAllocationGroup.val(),
                            'subGroup': $EventAllocationSubGroup.val(),
                            'product': $EventAllocationProduct.val(),
                            'tier': $EventAllocationTier.val(),
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
    }

    exports.run = run;

    return exports
});
