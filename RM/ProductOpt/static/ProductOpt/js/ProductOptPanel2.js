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
        bootstrap_table_group_by = require('bootstrap-table-group-by'),
        // filter_control = require('filter-control'),
        select2_filter = require('select2-filter');

    var exports = {},
        table_params = {};

    var $Panel2Table1ContainerId = $("#ProductOptPanel2Table1ContainerId"),
        $Panel2Table1Id = $("#ProductOptPanel2Table1Id");
    var $date = $("#date");

    function run () {
        init();
        event()
    }

    function init() {
        $.get('/RM/ProductOpt/panel1/form1/submit', function (res) {
            var status = res['status'],
                msg = res['msg'];
            if (status === 1){
                var columns = res['columns'];
                Panel2Table1_init(null, columns)
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
            row['date'] = $date.val();
            //Check for validations here on the front end
            $.get('/RM/ProductOpt/panel2/table1/edit', row,function () {
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
    }

    function Panel2Table1_init(date, columns) {
        tableExportInit();
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
            showExport:true,
            exportTypes:['json', 'xml', 'csv', 'txt', 'sql', 'xlsx'],
            // filterControl:true,
            undefinedText: '-',
            filter:true,
            // groupBy:true,
            // groupByField:'center_id',
            url:"/RM/ProductOpt/panel2/table1/create",
            //transferring the date from one panel to the other. Kind of like passing information betweeen Angular components
            queryParams: function (para) {
                para.date = date;
                table_params = para;
                tableExportEvent();
                return para
            },
            columns: columns,
            rowAttributes:function (row, index) {
            },
        });
    }

    function tableExportInit() {
        'use strict';
        var sprintf = $.fn.bootstrapTable.utils.sprintf;

        var TYPE_NAME = {
            json: 'JSON',
            xml: 'XML',
            png: 'PNG',
            csv: 'CSV',
            txt: 'TXT',
            sql: 'SQL',
            doc: 'MS-Word',
            excel: 'MS-Excel',
            xlsx: 'MS-Excel',
            powerpoint: 'MS-Powerpoint',
            pdf: 'PDF'
        };

        $.extend($.fn.bootstrapTable.defaults, {
            showExport: false,
            exportDataType: 'basic', // basic, all, selected
            // 'json', 'xml', 'png', 'csv', 'txt', 'sql', 'doc', 'excel', 'powerpoint', 'pdf'
            exportTypes: ['json', 'xml', 'csv', 'txt', 'sql', 'excel'],
            exportOptions: {}
        });

        $.extend($.fn.bootstrapTable.defaults.icons, {
            export: 'glyphicon-export icon-share'
        });

        $.extend($.fn.bootstrapTable.locales, {
            formatExport: function () {
                return 'Export data';
            }
        });
        $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales);

        var BootstrapTable = $.fn.bootstrapTable.Constructor,
            _initToolbar = BootstrapTable.prototype.initToolbar;

        BootstrapTable.prototype.initToolbar = function () {
            this.showToolbar = this.options.showExport;

            _initToolbar.apply(this, Array.prototype.slice.apply(arguments));

            if (this.options.showExport) {
                var that = this,
                    $btnGroup = this.$toolbar.find('>.btn-group'),
                    $export = $btnGroup.find('div.export');

                if (!$export.length) {
                    $export = $([
                        '<div class="export btn-group">',
                        '<button class="btn' +
                        sprintf(' btn-%s', this.options.buttonsClass) +
                        sprintf(' btn-%s', this.options.iconSize) +
                        ' dropdown-toggle" aria-label="export type" ' +
                        'title="' + this.options.formatExport() + '" ' +
                        'data-toggle="dropdown" type="button">',
                        sprintf('<i class="%s %s"></i> ', this.options.iconsPrefix, this.options.icons.export),
                        '<span class="caret"></span>',
                        '</button>',
                        '<ul class="dropdown-menu" role="menu">',
                        '</ul>',
                        '</div>'].join('')).appendTo($btnGroup);

                    var $menu = $export.find('.dropdown-menu'),
                        exportTypes = this.options.exportTypes;

                    if (typeof this.options.exportTypes === 'string') {
                        var types = this.options.exportTypes.slice(1, -1).replace(/ /g, '').split(',');

                        exportTypes = [];
                        $.each(types, function (i, value) {
                            exportTypes.push(value.slice(1, -1));
                        });
                    }
                    $.each(exportTypes, function (i, type) {
                        if (TYPE_NAME.hasOwnProperty(type)) {
                            $menu.append(['<li role="menuitem" data-type="' + type + '">',
                                '<a href="javascript:void(0)">',
                                TYPE_NAME[type],
                                '</a>',
                                '</li>'].join(''));
                        }
                    });
                }
            }
        };
    }

    function tableExportEvent() {
        var $menu = $('.export .dropdown-menu li');

        $menu.click(function () {
            var type = $(this).data('type'),
                extension;

            table_params.type = type;

            switch (type) {
                case 'excel':
                    extension = "xlsx";
                    break;
                case 'csv':
                    extension = 'csv';
                    break;
                case 'xlsx':
                    extension = 'xlsx';
                    break;
                case 'json':
                    extension = 'json';
                    break;
            }

            var url = '/RM/ProductOpt/panel2/table1/export/export.' + extension + '?' + $.param(table_params);
            window.location.href = url
        });
    }

    exports.run = run;
    exports.Panel2Table1_init = Panel2Table1_init;

    return exports
});
