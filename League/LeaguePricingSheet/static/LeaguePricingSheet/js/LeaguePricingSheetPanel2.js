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
        tableExport = require('tableExport'),
        x_editable = require('x-editable'),
        flat_json = require('flat-json'),
        multiple_sort = require('multiple-sort'),
        bootstrap_table_editable = require('bootstrap-table-editable'),
        bootstrap_table_group_by = require('bootstrap-table-group-by'),
        // filter_control = require('filter-control'),
        select2_filter = require('select2-filter');

    var exports = {};

    var $Panel2Table1ContainerId = $("#LeaguePricingSheetPanel2Table1ContainerId"),
        $Panel2Table1Id = $("#LeaguePricingSheetPanel2Table1Id");

    var $duration = $('#duration');

    function run () {
        init();
        event()
    }

    function init() {
        $.get('/League/LeaguePricingSheet/panel1/form1/submit', function (res) {
            var status = res['status'],
                msg = res['msg'];
            if (status === 1){
                var columns = res['columns'];
                Panel2Table1_init($duration.val(),columns)
            }else {
                alert(msg)
            }
        });
    }

    function event() {

        //editable events
        $Panel2Table1Id.on('editable-save.bs.table',function (editable, field, row, oldValue, $el) {

            row['field'] = field;
            row['old_value'] = oldValue;
            row['duration'] = $duration.val();

            $.get('/League/LeaguePricingSheet/panel2/table1/edit', row,function () {
                $Panel2Table1Id.bootstrapTable('refresh');
                var notice = new PNotify({
                                    title: 'Success!',
                                    text: 'You have successfully revise the data',
                                    type: 'success',
                                    sound: false,
                                    animate_speed: 'fast',
                                    styling: 'bootstrap3',
                                    nonblock: {
                                        nonblock: true
                                    }
                                });
                notice.get().click(function() {
                    notice.remove();
                });
            })
        });

        // Modal Events
        $('#add').click(function () {
            $('#LeaguePricingSheetPanel2Modal1AddCreate').click()
        });
        $('#LeaguePricingSheetPanel2Modal1AddFormId').submit(function (e) {
            var data = $(this).serialize();

            $.get('/League/LeaguePricingSheet/panel2/modal1/add', data,function () {
                $Panel2Table1Id.bootstrapTable('refresh');
                $('#LeaguePricingSheetPanel2Modal1AddNo').click();
                var notice = new PNotify({
                    title: 'Success!',
                    text: 'You have successfully revise the data',
                    type: 'success',
                    sound: false,
                    animate_speed: 'fast',
                    styling: 'bootstrap3',
                    nonblock: {
                        nonblock: true
                    }
                });
                notice.get().click(function() {
                    notice.remove();
                });
            });

            return false
        });
    }

    function Panel2Table1_init(duration, columns) {

        $Panel2Table1Id.bootstrapTable({
            height:600,
            striped:true,
            minimumCountColumns:2,
            showFooter:false,
            pagination:true,
            paginationLoop: true,
            sidePagination: 'server',
            // pageSize: 200,
            pageList: [10, 25, 50, 100, 'All'],
            showExport:true,
            exportTypes:['json', 'xml', 'csv', 'txt', 'sql', 'xlsx'],
            toolbar: '#LeaguePricingSheetPanel2Table1Toolbar',
            // filterControl:true,
            undefinedText: '-',
            filter:true,
            // groupBy:true,
            // groupByField:'center_id',
            url:"/League/LeaguePricingSheet/panel2/table1/create",
            queryParams: function (para) {
                para.duration = $duration.val();
                return para
            },
            columns: columns,
            rowAttributes:function (row, index) {
            },
        });
    }

    function mergeRows(index, field, rowspan) {

        $Panel2Table1Id.bootstrapTable('mergeCells', {
            index: index,
            field: field,
            rowspan: rowspan
        });
    }

    exports.run = run;
    exports.Panel2Table1_init = Panel2Table1_init;

    return exports
});
