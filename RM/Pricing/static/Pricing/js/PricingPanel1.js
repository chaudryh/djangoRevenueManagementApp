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

    var $Panel1Form1 = $("#PricingPanel1Form1"),
        $Panel1Form1Submit = $('#PricingPanel1Form1Submit'),
        $Panel1Table1Id = $("#PricingPanel1Table1Id");

    var exports = {};
    var select_center_list = [],
        is_search = false,
        table_params = {};

    // window.PricingPanel1Table1 = {};
    // PricingPanel1Table1.select_center_list = [];

    function run () {
        init();
        event()
    }

    function init() {
        $.get('/RM/Pricing/panel1/form1/submit', function (res) {
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
            $.get('/RM/Pricing/panel1/form1/submit',data,function (res) {
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
        tableExportInit();
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
            exportTypes:['csv', 'json', 'xlsx'],
            exportOptions:null,
            // filterControl:true,
            filter:true,
            url:"/RM/Pricing/panel1/table1/create",
            // maintainSelected: true,
            clickToSelect: true,
            columns: columns,
            queryParams: function (para) {
                para.product = product;
                para.as_of_date = as_of_date;
                table_params = para;
                tableExportEvent();

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

            var url = '/RM/Pricing/panel1/table1/export/export.' + extension + '?' + $.param(table_params);
            window.location.href = url
        });
    }

    exports.run = run;
    exports.Panel1Table1_init = Panel1Table1_init;

    return exports

});
