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

    var $Panel2Table1ContainerId = $("#LeagueCenterInfoPanel2Table1ContainerId"),
        $Panel2Table1Id = $("#LeagueCenterInfoPanel2Table1Id");

    var $Panel1Form1Dow = $('#DOW'),
        $Panel1Form1Type = $('#type'),
        $Panel1Form1SubType = $('#subType'),
        $Panel1Form1Start = $('#start'),
        $Panel1Form1End = $('#end'),
        $Panel1Form1dowRange = $('#dowRange'),
        $Panel1Form1dateRange = $('#dateRange'),
        $Panel1Form1Status = $('#status'),
        $Panel1Form1Distinct = $('#distinct');


    function run () {
        init();
        event()
    }

    function init() {

        // Init form
        $("#start").datepicker("setDate", moment()._d); // .subtract(6, 'days')
        $("#end").datepicker("setDate", moment()._d);

        $.get('/League/LeagueCenterInfo/panel2/table1/get_columns', function (res) {
            var status = res['status'],
                msg = res['msg'];
            if (status === 1){
                var columns = res['columns'];
                Panel2Table1_init(columns)
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

            $.get('/League/LeagueCenterInfo/panel2/table1/edit', row,function () {
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

        //expand table detail
        $Panel2Table1Id.on('expand-row.bs.table', function (e, index, row, $detail) {
            var center_id = row['center_id'],
                data={'center_id': center_id},
                refresh_id = 'Panel2Table1DetailRefresh' + index,
                table_id = 'Panel2Table1DetailTable' + index;

            $detail.html(
                '<div class="row" id="'+ refresh_id +'">' +
                '<div class="col-md-2 col-md-offset-5">' +
                '<i class="fa fa-spinner fa-pulse fa-3x fa-fw"></i>' +
                '</div>' +
                '</div>' +
                '<div class="row col-md-12 col-md-offset-2">' +
                '<table  id="'+ table_id +'"></table>' +
                '</div>'
            );

            var $refresh_id = $('#' + refresh_id),
                $table_id = $('#' + table_id);

            $.get('/League/LeagueCenterInfo/panel2/table1/get_columns_details', data, function (res) {
                var status = res['status'],
                    msg = res['msg'];
                if (status === 1){
                    var columns = res['columns'];
                    $refresh_id.hide();
                    $table_id.bootstrapTable('destroy');
                    Panel2Table1DetailTable_init($table_id, columns, center_id)
                }else {
                    alert(msg)
                }
            });
            // $detail.load(url_detail,data)
        });

        // Modal Events
        // $('#add').click(function () {
        //     $('#LeagueCenterInfoPanel2Modal1AddCreate').click()
        // });
        // $('#LeagueCenterInfoPanel2Modal1AddFormId').submit(function (e) {
        //     var data = $(this).serialize();
        //
        //     $.get('/League/LeagueCenterInfo/panel2/modal1/add', data,function () {
        //         $Panel2Table1Id.bootstrapTable('refresh');
        //         $('#LeagueCenterInfoPanel2Modal1AddNo').click();
        //         var notice = new PNotify({
        //             title: 'Success!',
        //             text: 'You have successfully revise the data',
        //             type: 'success',
        //             sound: false,
        //             animate_speed: 'fast',
        //             styling: 'bootstrap3',
        //             nonblock: {
        //                 nonblock: true
        //             }
        //         });
        //         notice.get().click(function() {
        //             notice.remove();
        //         });
        //     });
        //
        //     return false
        // });
    }

    function Panel2Table1_init(columns) {

        $Panel2Table1Id.bootstrapTable({
            height:600,
            striped:true,
            minimumCountColumns:2,
            showFooter:false,
            pagination:true,
            paginationLoop: true,
            sidePagination: 'server',
            pageSize: 10,
            pageList: [10, 25, 50, 100, 'All'],
            detailView: true,
            showExport:true,
            exportTypes:['json', 'xml', 'csv', 'txt', 'sql', 'xlsx'],
            // toolbar: '#LeagueCenterInfoPanel2Table1Toolbar',
            // filterControl:true,
            undefinedText: '-',
            filter:true,
            // groupBy:true,
            // groupByField:'center_id',
            url:"/League/LeagueCenterInfo/panel2/table1/create",
            queryParams: function (para) {
                para.dow = $Panel1Form1Dow.val();
                para.type = $Panel1Form1Type.val();
                para.subType = $Panel1Form1SubType.val();
                para.start = $Panel1Form1Start.val();
                para.end = $Panel1Form1End.val();
                para.dowRange = $Panel1Form1dowRange.val();
                para.dateRange = $Panel1Form1dateRange.val();
                para.status = $Panel1Form1Status.val();
                para.distinct = $Panel1Form1Distinct.val();

                return para
            },
            columns: columns,
            rowAttributes:function (row, index) {
            },
        });
    }

    function Panel2Table1DetailTable_init($table_id, columns, center_id) {
        $table_id.bootstrapTable({
            // height:600,
            striped:true,
            minimumCountColumns:2,
            showFooter:false,
            pagination:true,
            paginationLoop: true,
            sidePagination: 'server',
            pageSize: 10,
            pageList: [10, 25, 50, 100, 'All'],
            // detailView: true,
            showExport:true,
            exportTypes:['json', 'xml', 'csv', 'txt', 'sql', 'xlsx'],
            exportOptions:{'maxNestedTables': 0},
            // clickToSelect:true,
            // filterControl:true,
            undefinedText: '-',
            filter:true,
            // groupBy:true,
            // groupByField:'center_id',
            url:"/League/LeagueCenterInfo/panel2/table1/create_details",
            queryParams: function (para) {
                para.center_id = center_id;
                para.dow = $Panel1Form1Dow.val();
                para.type = $Panel1Form1Type.val();
                para.subType = $Panel1Form1SubType.val();
                para.start = $Panel1Form1Start.val();
                para.end = $Panel1Form1End.val();
                para.dowRange = $Panel1Form1dowRange.val();
                para.dateRange = $Panel1Form1dateRange.val();
                para.status = $Panel1Form1Status.val();
                para.distinct = $Panel1Form1Distinct.val();

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
