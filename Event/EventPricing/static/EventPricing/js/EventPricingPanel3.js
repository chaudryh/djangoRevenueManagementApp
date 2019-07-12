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
        select2_filter = require('select2-filter');

    var $Panel3Table1ContainerId = $("#EventPricingPanel3Table1ContainerId"),
        $Panel3Table1Id = $("#EventPricingPanel3Table1Id");

    var exports = {};

    function run () {
        init();
        event()
    }

    function init() {

        $Panel3Table1Id.bootstrapTable({
            height:600,
            striped:true,
            minimumCountColumns:2,
            showFooter:false,
            pagination:true,
            paginationLoop: true,
            sidePagination: 'server',
            // filterControl:true,
            undefinedText: '-',
            filter:true,
            url:"/Event/EventPricing/panel3/table1/create",
            columns:[
                [
                    {
                        field: 'center_id',
                        title: 'Id',
                        sortable: true,
                        align: 'center',
                        vlign: 'center',
                        rowspan: 2,
                        filter:{
                            type:'input'
                        }
                    },
                    {
                        field: 'center_name',
                        title: 'Name',
                        sortable: true,
                        align: 'center',
                        vlign: 'center',
                        rowspan: 2,
                        filter:{
                            type:'input'
                        }
                    },
                    {
                        field: 'product',
                        title: 'Product',
                        align: 'center',
                        rowspan: 2,
                        filter:{
                            type:'input'
                        }
                    },
                    {
                        field: 'monday',
                        title: 'Weekday',
                        colspan: 3,
                        align: 'center'
                    },
                    // {
                    //     field: 'tuesday',
                    //     title: 'Tuesday',
                    //     colspan: 3,
                    //     align: 'center'
                    // },
                    // {
                    //     field: 'wednesday',
                    //     title: 'Wednesday',
                    //     colspan: 3,
                    //     align: 'center'
                    // },
                    // {
                    //     field: 'thursday',
                    //     title: 'Thursday',
                    //     colspan: 3,
                    //     align: 'center'
                    // },
                    {
                        field: 'friday',
                        title: 'Friday',
                        colspan: 3,
                        align: 'center'
                    },
                    {
                        field: 'saturday',
                        title: 'Saturday',
                        colspan: 3,
                        align: 'center'
                    },
                    {
                        field: 'sunday',
                        title: 'Sunday',
                        colspan: 3,
                        align: 'center'
                    },
                ],
                [
                    {
                        field: 'monday-nonprime',
                        title: 'Non-Prime',
                        sortable: true,
                        editable: true,
                        align: 'center'
                    },
                    {
                        field: 'monday-prime',
                        title: 'Prime',
                        sortable: true,
                        editable: true,
                        align: 'center'
                    },
                    {
                        field: 'monday-premium',
                        title: 'Premium',
                        sortable: true,
                        editable: true,
                        align: 'center'
                    },
                    // {
                    //     field: 'tuesday-nonprime',
                    //     title: 'Non-Prime',
                    //     sortable: true,
                    //     editable: true,
                    //     align: 'center'
                    // },
                    // {
                    //     field: 'tuesday-prime',
                    //     title: 'Prime',
                    //     sortable: true,
                    //     editable: true,
                    //     align: 'center'
                    // },
                    // {
                    //     field: 'tuesday-premium',
                    //     title: 'Premium',
                    //     sortable: true,
                    //     editable: true,
                    //     align: 'center'
                    // },
                    // {
                    //     field: 'wednesday-nonprime',
                    //     title: 'Non-Prime',
                    //     sortable: true,
                    //     editable: true,
                    //     align: 'center'
                    // },
                    // {
                    //     field: 'wednesday-prime',
                    //     title: 'Prime',
                    //     sortable: true,
                    //     editable: true,
                    //     align: 'center'
                    // },
                    // {
                    //     field: 'wednesday-premium',
                    //     title: 'Premium',
                    //     sortable: true,
                    //     editable: true,
                    //     align: 'center'
                    // },
                    // {
                    //     field: 'thursday-nonprime',
                    //     title: 'Non-Prime',
                    //     sortable: true,
                    //     editable: true,
                    //     align: 'center'
                    // },
                    // {
                    //     field: 'thursday-prime',
                    //     title: 'Prime',
                    //     sortable: true,
                    //     editable: true,
                    //     align: 'center'
                    // },
                    // {
                    //     field: 'thursday-premium',
                    //     title: 'Premium',
                    //     sortable: true,
                    //     editable: true,
                    //     align: 'center'
                    // },
                    {
                        field: 'friday-nonprime',
                        title: 'Non-Prime',
                        sortable: true,
                        editable: true,
                        align: 'center'
                    },
                    {
                        field: 'friday-prime',
                        title: 'Prime',
                        sortable: true,
                        editable: true,
                        align: 'center'
                    },
                    {
                        field: 'friday-premium',
                        title: 'Premium',
                        sortable: true,
                        editable: true,
                        align: 'center'
                    },
                    {
                        field: 'saturday-nonprime',
                        title: 'Non-Prime',
                        sortable: true,
                        editable: true,
                        align: 'center'
                    },
                    {
                        field: 'saturday-prime',
                        title: 'Prime',
                        sortable: true,
                        editable: true,
                        align: 'center'
                    },
                    {
                        field: 'saturday-premium',
                        title: 'Premium',
                        sortable: true,
                        editable: true,
                        align: 'center'
                    },
                    {
                        field: 'sunday-nonprime',
                        title: 'Non-Prime',
                        sortable: true,
                        editable: true,
                        align: 'center'
                    },
                    {
                        field: 'sunday-prime',
                        title: 'Prime',
                        sortable: true,
                        editable: true,
                        align: 'center'
                    },
                    {
                        field: 'sunday-premium',
                        title: 'Premium',
                        sortable: true,
                        editable: true,
                        align: 'center'
                    },
                ],

            ],
            rowAttributes:function (row, index) {
            },
        });
    }

    function event() {

        //merge cells
        $Panel3Table1Id.on('load-success.bs.table column-switch.bs.table page-change.bs.table search.bs.table', function () {
            var table = $Panel3Table1Id[0];
            var rowLength = table.rows.length;
            var count = 0;
            var row = table.rows[2].cells[0].innerHTML;
            var saveIndex = 0;

            // mergeRows(3, 'center_id', 2);
            // mergeRows(3, 'center_name', 2);

            for (var i = 2; i < rowLength; i++) {
                if (row === table.rows[i].cells[0].innerHTML) {
                    count++;

                    if(i === rowLength - 1) {
                        mergeRows(saveIndex, 'center_id', count);
                        mergeRows(saveIndex, 'center_name', count);
                    }
                } else {

                    mergeRows(saveIndex, 'center_id', count);
                    mergeRows(saveIndex, 'center_name', count);

                    row = table.rows[i].cells[0].innerHTML;
                    saveIndex = i-2;
                    count = 1;
                }
            }
        });

        //editable events
        $Panel3Table1Id.on('editable-save.bs.table',function (editable, field, row, oldValue, $el) {

            row['field'] = field;

            $.get('/Event/EventPricing/panel3/table1/edit', row,function () {
                $Panel3Table1Id.bootstrapTable('refresh');
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
    }

    function mergeRows(index, field, rowspan) {

        $Panel3Table1Id.bootstrapTable('mergeCells', {
            index: index,
            field: field,
            rowspan: rowspan
        });
    }

    exports.run = run;

    return exports
});
