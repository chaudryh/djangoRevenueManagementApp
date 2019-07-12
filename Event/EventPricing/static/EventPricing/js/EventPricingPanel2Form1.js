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
        select2_filter = require('select2-filter'),
        EventPricingPanel1 = require('/static/EventPricing/js/EventPricingPanel1.js');

    var exports = {};
    var timeOut;
    var product_ids = ['3001', '3002', '3003', '3004', '3005', '3006', '3007',
                        '3201', '3202', '3203', '3204', '3205', '3206', '3207', '3208', '3209'
                        ];

    var $Panel2Form1 = $('#EventPricingPanel2Form1'),
        $Panel2Form1Submit = $('#EventPricingPanel2Form1Submit'),
        $Panel1Table1Id = $('#EventPricingPanel1Table1Id'),
        $Panel2Form1a = $('#EventPricingPanel2Form1a'),
        $Panel2Form1b = $('#EventPricingPanel2Form1b'),
        $Panel2Form1c = $('#EventPricingPanel2Form1c'),
        $Panel2Form1d = $('#EventPricingPanel2Form1d');

    var $Panel2Form1Product = $('#product'),
        $Panel2Form1Start = $('#start'),
        $Panel2Form1End = $('#end'),
        $Panel2Form1DOW = $('#DOW'),
        $Panel2Form1InputDOW = $('#form-input-DOW'),

        $Panel2Form1NpPriceSymbol = $('#np-price-symbol'),
        $Panel2Form1PrimewkPriceSymbol = $('#primewk-price-symbol'),
        $Panel2Form1PrimewkdPriceSymbol = $('#primewkd-price-symbol'),
        $Panel2Form1PremiumPriceSymbol = $('#premium-price-symbol'),
        $Panel2Form1NpPrice = $('#np-price'),
        $Panel2Form1PrimewkPrice = $('#primewk-price'),
        $Panel2Form1PrimewkdPrice = $('#primewkd-price'),
        $Panel2Form1PremiumPrice = $('#premium-price'),
        $Panel2Form1NpPriceUnit = $('#np-price-unit'),
        $Panel2Form1PrimewkPriceUnit = $('#primewk-price-unit'),
        $Panel2Form1PrimewkdPriceUnit = $('#primewkd-price-unit'),
        $Panel2Form1PremiumPriceUnit = $('#premium-price-unit'),
        $Panel2Form1NpPriceBase = $('#np-price-base'),
        $Panel2Form1PrimewkPriceBase = $('#primewk-price-base'),
        $Panel2Form1PrimewkdPriceBase = $('#primewkd-price-base'),
        $Panel2Form1PremiumPriceBase = $('#premium-price-base'),
        $Panel2Form1wkPriceSymbol = $('#wk-price-symbol'),
        $Panel2Form1wkndPriceSymbol = $('#wknd-price-symbol'),
        $Panel2Form1wkPrice = $('#wk-price'),
        $Panel2Form1wkndPrice = $('#wknd-price'),
        $Panel2Form1wkPriceUnit = $('#wk-price-unit'),
        $Panel2Form1wkndPriceUnit = $('#wknd-price-unit'),
        $Panel2Form1wkPriceBase = $('#wk-price-base'),
        $Panel2Form1wkndPriceBase = $('#wknd-price-base');

    function run () {
        init();
        event()
    }

    function init() {
        $Panel2Form1DOW.select2({
            placeholder: "Default To All"
        });

        $Panel2Form1Product.select2({
            allowClear: false
        });
    }

    function event() {
        // Form1 Change events
        $Panel2Form1Product.change(function () {

            clear_form();
            $.get('/Event/EventPricing/panel1/form1/submit', {'product': $Panel2Form1Product.val()}, function (res) {
                var status = res['status'],
                    msg = res['msg'];
                if (status === 1){
                    $Panel1Table1Id.bootstrapTable('destroy');
                    var columns = res['columns'];
                    EventPricingPanel1.Panel1Table1_init($Panel2Form1Product.val(), null,columns)
                }else {
                    alert(msg)
                }
            });

            // Form change
            if ( $Panel2Form1Product.val() === 'event bowling') {
                $Panel2Form1a.show();
                $Panel2Form1b.hide();
                $Panel2Form1c.hide();
                $Panel2Form1d.hide();
            }
            else if ( $Panel2Form1Product.val() === 'event shoe') {
                $Panel2Form1a.hide();
                $Panel2Form1b.show();
                $Panel2Form1c.hide();
                $Panel2Form1d.hide();
            }
            else if ( $Panel2Form1Product.val() === 'event basic packages') {
                $Panel2Form1a.hide();
                $Panel2Form1b.hide();
                $Panel2Form1c.hide();
                $Panel2Form1d.show();
            }
            else {
                $Panel2Form1a.show();
                $Panel2Form1b.hide();
                $Panel2Form1c.hide();
                $Panel2Form1d.hide();
            }

            // DOW change
            if ( $.inArray($Panel2Form1Product.val(), ['event bowling', 'event shoe', 'event basic packages']) === -1) {
                $Panel2Form1InputDOW.hide();
            }
            else {
                $Panel2Form1InputDOW.show();
            }
        });

        $Panel2Form1Start.change(function () {
            var formats = [
                'MM/DD/YY'
            ];
            var start = $Panel2Form1Start.val();
            var is_date = moment(start, formats, true).isValid();
            if (is_date || start.length === 0) {
                $.get('/Event/EventPricing/panel1/form1/submit', {'product': $Panel2Form1Product.val()}, function (res) {
                    var status = res['status'],
                        msg = res['msg'];
                    if (status === 1){
                        $Panel1Table1Id.bootstrapTable('destroy');
                        var columns = res['columns'];
                        EventPricingPanel1.Panel1Table1_init($Panel2Form1Product.val(), $Panel2Form1Start.val(),columns)
                    }else {
                        alert(msg)
                    }
                });
            }
        });

        // Form1 Submit events
        $Panel2Form1.submit(function (e) {

            var data = $(this).serializeArray(),
                centers = $Panel1Table1Id.bootstrapTable('getAllSelections'),
                centers_list = [];
            clearTimeout(timeOut);

            centers.forEach(function (center) {
                centers_list.push(center['center_id'])
            });
            data.push({name: 'centers', value: centers_list});

            $Panel2Form1Submit.html("Saving...");
            $.get('/Event/EventPricing/panel2/form1/submit',data,function (res) {

                clear_form();
                $.get('/Event/EventPricing/panel1/form1/submit', {'product': $Panel2Form1Product.val()}, function (res) {
                    var status = res['status'],
                        msg = res['msg'];
                    if (status === 1){
                        $Panel1Table1Id.bootstrapTable('destroy');
                        var columns = res['columns'];
                        EventPricingPanel1.Panel1Table1_init($Panel2Form1Product.val(), null, columns)
                    }else {
                        alert(msg)
                    }
                });

                var status = res['status'],
                    msg = res['msg'];
                if (status === 1){
                    $Panel2Form1Submit.html("Saved");
                    if (msg !== '') {
                        alert(msg)
                    }
                    timeOut = setTimeout(function() {
                        $Panel1Form1Submit.html("Submit");
                    }, 2000);
                }else {
                    $Panel2Form1Submit.html("Try Again");
                    alert(msg)
                }
            });

            return false
        });

        // Form1a change events
        product_ids.forEach(function (product_id) {
            $('#'+ product_id +'-price-symbol').change(function () {
                if ($('#'+ product_id +'-price-symbol').val() === 'equal') {
                    $('#'+ product_id +'-price-base').prop( 'disabled', true);
                    $('#'+ product_id +'-price-base').hide()
                }
                else {
                    $('#'+ product_id +'-price-base').prop( 'disabled', false);
                    $('#'+ product_id +'-price-base').show()

                }
            });
        });
    }

    function clear_form () {
        // clear form 1
        $Panel2Form1Start.val('');
        $Panel2Form1End.val('');
        $Panel2Form1DOW.val(null).trigger('change');
        // clear form 1a
        product_ids.forEach(function (product_id) {
            $('#'+ product_id +'-price-symbol').val('plus');
            $('#'+ product_id +'-price').val('');
            $('#'+ product_id +'-unit');
            $('#'+ product_id +'-price-base').val(product_id);
            $('#'+ product_id +'-price-base').prop( 'disabled', false);
            $('#'+ product_id +'-price-base').show();
        });

        // clear form 1b
        $('#price-symbol').val('plus');
        $('#price').val('');
        $('#price-unit').val('dollar');
    }

    exports.run = run;

    return exports
});
