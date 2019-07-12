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

    var $Panel2Table1ContainerId = $("#BundlePanel2Table1ContainerId"),
        $Panel2Table1Id = $("#BundlePanel2Table1Id");

    var $date = $('#date'),
        $price_type = $('#price_type');

    function run () {
        init();
        event()
    }

    function init() {
        Panel2Table1_init_auto()
    }

    function event() {

        //editable events
        //$el is the html/css selector for the editable pop-up from bootstrap's x-editable library
        $Panel2Table1Id.on('editable-save.bs.table',function (editable, field, row, oldValue, $el) {

            row['field'] = field;
            row['old_value'] = oldValue;
            row['price_type'] = $price_type.val();
            row['date'] = $date.val();

            $.get('/RM/Bundle/panel2/table1/edit', row,function () {
                $Panel2Table1Id.bootstrapTable('refresh');
                var notice = new PNotify({
                                    title: 'Success!',
                                    text: 'You have successfully revised the data',
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
            var bundle_id = row['bundle_id'],
                data={'bundle_id': bundle_id},
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

            var $refresh_id = $('#' + refresh_id), //shows spinner before table row expansion
                $table_id = $('#' + table_id);

            $.get('/RM/Bundle/panel2/table1/create_details_columns', data, function (res) {
                var status = res['status'],
                    msg = res['msg'];
                if (status === 1){
                    var columns = res['columns'];
                    $refresh_id.hide();
                    $table_id.bootstrapTable('destroy');
                    Panel2Table1DetailTable_init($table_id, columns, bundle_id)
                }else {
                    alert(msg)
                }
            });
            // $detail.load(url_detail,data)
        });
    }

    function Panel2Table1_init_auto() {
        var data = {'date': $date.val(), 'price_type': $price_type.val()};
        $.get('/RM/Bundle/panel2/table1/create_columns', data, function (res) {
            var status = res['status'],
                msg = res['msg'];
            if (status === 1){
                var columns = res['columns'];
                $Panel2Table1Id.bootstrapTable('destroy');
                Panel2Table1_init(columns)
            }else {
                alert(msg)
            }
        });
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
            pageSize: 25,
            pageList: [10, 25, 50, 100, 'All'],
            detailView: true,
            showExport:true,
            exportTypes:['json', 'xml', 'csv', 'txt', 'sql', 'xlsx'],
            clickToSelect:true,
            // filterControl:true,
            undefinedText: '-',
            filter:true,
            // groupBy:true,
            // groupByField:'center_id',
            url:"/RM/Bundle/panel2/table1/create",
            queryParams: function (para) {
                para.date = $date.val();
                para.price_type = $price_type.val();
                return para
            },
            columns: columns,
            rowAttributes:function (row, index) {
            },
        });
    }

    function Panel2Table1DetailTable_init($table_id, columns, bundle_id) {
        //table_id is used to pass and select sub-table in row expansion
        $table_id.bootstrapTable({
            // height:600,
            striped:true,
            minimumCountColumns:2,
            showFooter:false,
            pagination:true,
            paginationLoop: true,
            onlyInfoPagination: true,
            sidePagination: 'server',
            pageSize: 100,
            pageList: [10, 25, 50, 100, 'All'],
            // detailView: true,
            // showExport:true,
            // clickToSelect:true,
            // filterControl:true,
            undefinedText: '-',
            filter:true,
            // groupBy:true,
            // groupByField:'center_id',
            url:"/RM/Bundle/panel2/table1/create_details",
            queryParams: function (para) {
                para.bundle_id = bundle_id;
                return para
            },
            columns: columns,
            rowAttributes:function (row, index) {
            },
        });
    }
    //not used in promo page
    function mergeRows(index, field, rowspan) {

        $Panel2Table1Id.bootstrapTable('mergeCells', {
            index: index,
            field: field,
            rowspan: rowspan
        });
    }
    //similar to export in Angular. Allows the sharing of files by various components
    exports.run = run;
    exports.Panel2Table1_init = Panel2Table1_init;

    return exports
});
