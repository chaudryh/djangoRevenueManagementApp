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

    var $Panel2Table1ContainerId = $("#FoodPanel2Table1ContainerId"),
        $Panel2Table1Id = $("#FoodPanel2Table1Id");

    function run () {
        init();
        event()
    }

    function init() {
        Panel2Table1_init_auto()
    }

    function event() {

        //editable events
        $Panel2Table1Id.on('editable-save.bs.table',function (editable, field, row, oldValue, $el) {

            row['field'] = field;
            row['old_value'] = oldValue;

            $.get('/RM/Food/panel2/table1/edit', row,function () {
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

        // Modal events
        // Food
        $('#FoodAdd').click(function () {
            $('#FoodPanel2Modal1FoodAddCreate').click()
        });
        $('#FoodDelete').click(function () {
            $('#FoodPanel2Modal1FoodDeleteCreate').click()
        });
        $('#FoodPanel2Modal1FoodAddFormId').submit(function (e) {
            var data = $(this).serialize();

            $.get('/RM/Food/panel2/modal1food/add', data,function () {
                $Panel2Table1Id.bootstrapTable('refresh');
                $('#FoodPanel2Modal1FoodAddNo').click();
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
        $('#FoodPanel2Modal1FoodDeleteFormId').submit(function (e) {
            var data = [];
            var selections = $Panel2Table1Id.bootstrapTable('getAllSelections');

            data.push({name: 'selections', value: JSON.stringify(selections)});

            $.get('/RM/Food/panel2/modal1food/delete', data,function () {
                $Panel2Table1Id.bootstrapTable('refresh');
                $('#FoodPanel2Modal1FoodDeleteNo').click();
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
        // Menu
        $('#MenuAdd').click(function () {
            $('#FoodPanel2Modal2MenuAddCreate').click()
        });
        $('#MenuEdit').click(function () {
            $('#FoodPanel2Modal2MenuEditCreate').click()
        });
        $('#MenuDelete').click(function () {
            $('#FoodPanel2Modal2MenuDeleteCreate').click()
        });
        $('#FoodPanel2Modal2MenuAddFormId').submit(function (e) {
            var data = $(this).serialize();

            $.get('/RM/Food/panel2/modal2menu/add', data,function () {
                Panel2Table1_init_auto();
                $('#FoodPanel2Modal2MenuAddNo').click();
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
        $('#FoodPanel2Modal2MenuEditFormId').submit(function (e) {
            var data = $(this).serialize();

            $.get('/RM/Food/panel2/modal2menu/edit', data,function () {
                Panel2Table1_init_auto();
                $('#FoodPanel2Modal2MenuEditNo').click();
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
        $('#FoodPanel2Modal2MenuDeleteFormId').submit(function (e) {
            var data = $(this).serialize();

            $.get('/RM/Food/panel2/modal2menu/delete', data,function () {
                Panel2Table1_init_auto();
                $('#FoodPanel2Modal2MenuDeleteNo').click();
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
        // Tier
        $('#TierAdd').click(function () {
            $('#FoodPanel2Modal3TierAddCreate').click()
        });
        $('#TierEdit').click(function () {
            $('#FoodPanel2Modal3TierEditCreate').click()
        });
        $('#TierDelete').click(function () {
            $('#FoodPanel2Modal3TierDeleteCreate').click()
        });
        $('#FoodPanel2Modal3TierAddFormId').submit(function (e) {
            var data = $(this).serialize();

            $.get('/RM/Food/panel2/modal3tier/add', data,function () {
                Panel2Table1_init_auto();
                $('#FoodPanel2Modal3TierAddNo').click();
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
        $('#FoodPanel2Modal3TierEditFormId').submit(function (e) {
            var data = $(this).serialize();

            $.get('/RM/Food/panel2/modal3tier/edit', data,function () {
                Panel2Table1_init_auto();
                $('#FoodPanel2Modal3TierEditNo').click();
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
        $('#FoodPanel2Modal3TierDeleteFormId').submit(function (e) {
            var data = $(this).serialize();

            $.get('/RM/Food/panel2/modal3tier/delete', data,function () {
                Panel2Table1_init_auto();
                $('#FoodPanel2Modal3TierDeleteNo').click();
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

    function Panel2Table1_init_auto() {
        $.get('/RM/Food/panel1/form1/submit', function (res) {
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

    function Panel2Table1_init(columns, date, food_menu) {
        $Panel2Table1Id.bootstrapTable({
            height:600,
            striped:true,
            minimumCountColumns:2,
            showFooter:false,
            pagination:true,
            paginationLoop: true,
            sidePagination: 'server',
            pageSize: 200,
            pageList: ['All'],
            showExport:true,
            exportTypes:['json', 'xml', 'csv', 'txt', 'sql', 'xlsx'],
            clickToSelect:true,
            toolbar: '#FoodPanel2Table1Toolbar',
            // filterControl:true,
            undefinedText: '-',
            filter:true,
            // groupBy:true,
            // groupByField:'center_id',
            url:"/RM/Food/panel2/table1/create",
            queryParams: function (para) {
                para.food_menu = food_menu;
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
