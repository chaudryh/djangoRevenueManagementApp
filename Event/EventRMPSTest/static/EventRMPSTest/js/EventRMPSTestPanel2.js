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
        qTip2 = require('qTip2'),
        // bootstrap table extensions
        bootstrap_table_export = require('bootstrap-table-export'),
        // tableExport = require('tableExport'),
        x_editable = require('x-editable'),
        flat_json = require('flat-json'),
        multiple_sort = require('multiple-sort'),
        bootstrap_table_editable = require('bootstrap-table-editable'),
        bootstrap_table_group_by = require('bootstrap-table-group-by'),
        // filter_control = require('filter-control'),
        select2_filter = require('select2-filter');

    var exports = {};

    var $Panel2Table1ContainerId = $("#EventRMPSTestPanel2Table1ContainerId"),
        $Panel2Table1Id = $("#EventRMPSTestPanel2Table1Id");

    var $EventAllocationSaleRegion = $("#sale_region"),
        $EventAllocationTerritory = $("#territory"),
        $EventAllocationCenterId = $("#center_id"),
        $EventAllocationCenterName = $("#center_name"),
        $EventAllocationColumns = $("#columns");

    function run () {
        init();
        event()
    }

    function init() {
        $.get('/Event/EventRMPSTest/panel1/form1/submit', function (res) {
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
            // row['sale_region'] = $EventAllocationSaleRegion.val();
            // row['territory'] = $EventAllocationTerritory.val();
            // row['center_id'] = $EventAllocationCenterId.val();
            // row['center_name'] = $EventAllocationCenterName.val();
            // row['columns'] = $EventAllocationColumns.val();
            row['old_value'] = oldValue;

            var data = {};
            data['field'] = field;
            data['old_value'] = oldValue;
            data['arcade_type'] = row['arcade_type'];
            data['center_id'] = row['center_id'];
            data['center_name'] = row['center_name'];
            data['sale_region'] = row['sale_region'];
            data['territory'] = row['territory'];
            data[field] = row[field];

            $.get('/Event/EventRMPSTest/panel2/table1/edit', data, function (res) {
                $Panel2Table1Id.bootstrapTable('refresh');
                var status = res['status'],
                    msg = res['msg'];
                if (status === 1){
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
                }else {
                    alert(msg)
                }

            })
        });

        // $(window).resize(function () {
        //     $Panel2Table1Id.bootstrapTable('resetView');
        // });
    }

    function Panel2Table1_init(columns) {
        $Panel2Table1Id.bootstrapTable({
            // height:700,
            striped:true,
            minimumCountColumns:2,
            showFooter:false,
            pagination:true,
            paginationLoop: true,
            sidePagination: 'server',
            pageSize: 20,
            pageList: [10, 20, 25, 50, 100, 'All'],
            // filterControl:true,
            undefinedText: '-',
            showExport:true,
            exportTypes:['json', 'xml', 'csv', 'txt', 'sql', 'xlsx'],
            filter:true,
            // groupBy:true,
            // groupByField:'center_id',
            url:"/Event/EventRMPSTest/panel2/table1/create",
            queryParams: function (para) {
                para.sale_region = $EventAllocationSaleRegion.val();
                para.territory = $EventAllocationTerritory.val();
                para.center_id = $EventAllocationCenterId.val();
                para.center_name = $EventAllocationCenterName.val();
                para.columns = $EventAllocationColumns.val();

                return para
            },
            columns: columns,
            rowAttributes:function (row, index) {
            },
            onLoadSuccess:function () {
                $Panel2Table1Id.find('tbody tr').each(function (index) {
                    var $tr = $(this);
                    var centerId = $tr.find('td')[0].innerText;
                    // var centerName = $tr.find('td')[1].innerText;

                    $tr.find('td').each(function () {
                        $(this).qtip(
                            {
                                content: {
                                    text: '#' + centerId
                                    // text: centerId + '-' + centerName
                                },
                                position: {
                                    my: 'right middle',
                                    at: 'left middle',
                                },
                                style: {
                                    classes: 'qtip-rounded qtip-bootstrap'
                                },
                                events: {
                                    // show: function(event, api) {
                                    //     // $('.hideMe').hide();
                                    // },
                                    // hidden: function(event, api) {
                                    //     // $('.qtip').destroy();
                                    // }
                                },
                            }
                        );

                        // $(this).hover(
                        //     function () {
                        //         var $td = $(this);
                        //         // $(this).tooltip('show')
                        //         // console.log($(this))
                        //     },
                        //     function () {
                        //         var $tr = $(this);
                        //
                        //         // console.log($(this))
                        //     }
                        // );

                        // $(this).tooltip({'content': "done done"});
                        // $(this).tooltip({title: "Center " + centerId, placement: "auto", trigger:"click"});
                        // $(this).on('shown.bs.tooltip', function () {
                        //     var tooltipId = $(this).attr('aria-describedby');
                        //     // $('#' + tooltipId).appendTo($Panel2Table1Id)
                        // })
                    });
                    // console.log($(this)[0])
                })
                // $Panel2Table1Id.bootstrapTable('resetView')
                // var bt = $Panel2Table1ContainerId.find('.fixed-table-toolbar .pull-right');
                // bt.find('i').html('download')
                // bt.addClass('pull-left');
                // bt.removeClass('pull-right')
            }
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
