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
        // filter_control = require('filter-control'),
        select2_filter = require('select2-filter');

    var exports = {},
        table_params;

    var $Panel1Table1ContainerId = $("#EventPricingTablePanel1Table1ContainerId"),
        $Panel1Table1Id = $("#EventPricingTablePanel1Table1Id");

    function run () {
        init();
        event()
    }

    function init() {
        $.get('/Event/EventPricingTable/panel2/form1/submit', function (res) {
            var status = res['status'],
                msg = res['msg'];
            if (status === 1){
                var columns = res['columns'];
                Panel1Table1_init(null,null,columns)
            }else {
                alert(msg)
            }
        });
    }

    function event() {

        //merge cells
        $Panel1Table1Id.on('load-success.bs.table column-switch.bs.table page-change.bs.table search.bs.table', function () {
            var table = $Panel1Table1Id[0];
            var rowLength = table.rows.length;
            var count = 0;
            var row = table.rows[1].cells[0].innerHTML;
            var saveIndex = 0;

            // mergeRows(3, 'center_id', 2);
            // mergeRows(3, 'center_name', 2);

            for (var i = 1; i < rowLength; i++) {
                if (row === table.rows[i].cells[0].innerHTML) {
                    count++;

                    if(i === rowLength - 1) {
                        mergeRows(saveIndex, 'center_id', count);
                        mergeRows(saveIndex, 'center_name', count);
                        mergeRows(saveIndex, 'district', count);
                        mergeRows(saveIndex, 'region', count);
                        mergeRows(saveIndex, 'brand', count);
                        mergeRows(saveIndex, 'bowling_event_tier', count);
                        mergeRows(saveIndex, 'food_tier', count);
                        mergeRows(saveIndex, 'food_menu', count);
                    }
                } else {

                    mergeRows(saveIndex, 'center_id', count);
                    mergeRows(saveIndex, 'center_name', count);
                    mergeRows(saveIndex, 'district', count);
                    mergeRows(saveIndex, 'region', count);
                    mergeRows(saveIndex, 'brand', count);
                    mergeRows(saveIndex, 'bowling_event_tier', count);
                    mergeRows(saveIndex, 'food_tier', count);
                    mergeRows(saveIndex, 'food_menu', count);

                    row = table.rows[i].cells[0].innerHTML;
                    saveIndex = i-1;
                    count = 1;
                }
            }
        });

        //editable events
        $Panel1Table1Id.on('editable-save.bs.table',function (editable, field, row, oldValue, $el) {

            row['field'] = field;
            row['old_value'] = oldValue;

            $.get('/Event/EventPricingTable/panel1/table1/edit', row,function () {
                $Panel1Table1Id.bootstrapTable('refresh');
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

    function Panel1Table1_init(start, end, columns) {
        table_export_custom();
        $Panel1Table1Id.bootstrapTable({
            height:600,
            striped:true,
            minimumCountColumns:2,
            showFooter:false,
            pagination:true,
            paginationLoop: true,
            sidePagination: 'server',
            showExport:true,
            pageList: [10, 25, 50, 100, 'All'],
            exportTypes:['csv', 'json', 'xlsx'],
            exportOptions:null,
            // filterControl:true,
            undefinedtext: '-',
            filter:true,
            url:"/Event/EventPricingTable/panel1/table1/create",
            queryParams: function (para) {
                para.start = start;
                para.end = end;
                para.product = $("#product").val();
                table_params = para;
                return para
            },
            columns: columns,
        });
    }

    function mergeRows(index, field, rowspan) {

        $Panel1Table1Id.bootstrapTable('mergeCells', {
            index: index,
            field: field,
            rowspan: rowspan
        });
    }

    function table_export_custom() {
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
            xlsx: 'MS-Excel (OpenXML)',
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

                    $menu.find('li').click(function () {
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

                        window.location.href = '/Event/EventPricingTable/panel1/table1/export/export.' + extension + '?' + $.param(table_params)
                    });
                }
            }
        };
    }


    exports.run = run;
    exports.Panel1Table1_init = Panel1Table1_init;

    return exports
});
