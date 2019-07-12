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
        // filter_control = require('filter-control'),
        select2_filter = require('select2-filter');

    var $Panel1Form1 = $("#EventPricingPanel1Form1"),
        $Panel1Form1Submit = $('#EventPricingPanel1Form1Submit'),
        $Panel1Table1Id = $("#EventPricingPanel1Table1Id");

    var exports = {};
    var select_center_list = [],
        is_search = false;

    function run () {
        init();
        event()
    }

    function init() {
        $.get('/Event/EventPricing/panel1/form1/submit', function (res) {
            var status = res['status'],
                msg = res['msg'];
            if (status === 1){
                var columns = res['columns'];
                Panel1Table1_init(null, null, columns)
            }else {
                alert(msg)
            }
        });
    }

    function event() {

        $Panel1Form1.submit(function (e) {

            var data = $(this).serialize();

            $Panel1Form1Submit.html("Filtering...");
            $.get('/Event/EventPricing/panel1/form1/submit',data,function (res) {
                var status = res['status'],
                    msg = res['msg'];
                if (status === 1){
                    $Panel1Form1Submit.html("Filtered");
                    Panel1Table1_init();
                }else {
                    $Panel1Form1Submit.html("Try Again");
                    alert(msg)
                }
            });

            return false
        });
    }

    function Panel1Table1_init (product, as_of_date, columns) {
        $Panel1Table1Id.bootstrapTable({
            height:350,
            striped:true,
            minimumCountColumns:2,
            showFooter:false,
            pagination:true,
            paginationLoop: true,
            onlyInfoPagination: true,
            sidePagination: 'server',
            pageSize: '300',
            pageList: [10, 25, 50, 300, 'All'],
            showExport:true,
            exportTypes:['json', 'xml', 'csv', 'txt', 'sql', 'xlsx'],
            // filterControl:true,
            filter:true,
            url:"/Event/EventPricing/panel1/table1/create",
            // maintainSelected: true,
            clickToSelect: true,
            columns: columns,
            queryParams: function (para) {
                para.product = product;
                para.as_of_date = as_of_date;
                return para
            },
            rowAttributes:function (row, index) {
            },
            onCheckAll: function (rows) {
                select_center_list = [];
                rows.forEach(function (row) {select_center_list.push(row['center_id'])});
            },
            onUncheckAll: function () {
                select_center_list = [];
            },
            onCheck: function (row, $element) {
                var index = select_center_list.indexOf(row['center_id']);
                if (index === -1) select_center_list.push(row['center_id']);
            },
            onUncheck: function (row, $element) {
                var index = select_center_list.indexOf(row['center_id']);
                if (index !== -1) select_center_list.splice(index, 1);
            },
            onPageChange: function (data) {
                is_search = true;
            },
            onLoadSuccess: function (data) {
                if (is_search) {
                    $Panel1Table1Id.bootstrapTable('checkBy', {'field': 'center_id', 'values': select_center_list});
                    is_search = false
                }
                else {
                    select_center_list = [];
                }
            },
        });
    }

    exports.run = run;
    exports.Panel1Table1_init = Panel1Table1_init;

    return exports

});
