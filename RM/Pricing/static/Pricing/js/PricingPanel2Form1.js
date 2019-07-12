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
        select2_filter = require('select2-filter'),
        PricingPanel1 = require('/static/Pricing/js/PricingPanel1.js');

    var exports = {};
    var timeOut;

    var $Panel2Form1 = $('#PricingPanel2Form1'),
        $Panel2Form1Submit = $('#PricingPanel2Form1Submit'),
        $Panel1Table1Id = $('#PricingPanel1Table1Id'),
        $Panel2Form1a = $('#PricingPanel2Form1a'),
        $Panel2Form1b = $('#PricingPanel2Form1b'),
        $Panel2Form1c = $('#PricingPanel2Form1c'),
        $Panel2Form1AfterPartyFriday = $('#PricingPanel2Form1AfterPartyFriday');

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
        $Panel2Form1wkndPriceBase = $('#wknd-price-base'),
        $Panel2Form18pmPriceSymbol = $('#8pm-price-symbol'),
        $Panel2Form19pmPriceSymbol = $('#9pm-price-symbol'),
        $Panel2Form110pmPriceSymbol = $('#10pm-price-symbol'),
        $Panel2Form111pmPriceSymbol = $('#11pm-price-symbol'),
        $Panel2Form18pmPrice = $('#8pm-price'),
        $Panel2Form19pmPrice = $('#9pm-price'),
        $Panel2Form110pmPrice = $('#10pm-price'),
        $Panel2Form111pmPrice = $('#11pm-price'),
        $Panel2Form18pmPriceUnit = $('#8pm-price-unit'),
        $Panel2Form19pmPriceUnit = $('#9pm-price-unit'),
        $Panel2Form110pmPriceUnit = $('#10pm-price-unit'),
        $Panel2Form111pmPriceUnit = $('#11pm-price-unit'),
        $Panel2Form18pmPriceBase = $('#8pm-price-base'),
        $Panel2Form19pmPriceBase = $('#9pm-price-base'),
        $Panel2Form110pmPriceBase = $('#10pm-price-base'),
        $Panel2Form111pmPriceBase = $('#11pm-price-base');


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
            $.get('/RM/Pricing/panel1/form1/submit', {'product': $Panel2Form1Product.val()}, function (res) {
                var status = res['status'],
                    msg = res['msg'];
                if (status === 1){
                    $Panel1Table1Id.bootstrapTable('destroy');
                    var columns = res['columns'];
                    PricingPanel1.Panel1Table1_init($Panel2Form1Product.val(), null,columns)
                }else {
                    alert(msg)
                }
            });

            // Form change
            if ( $Panel2Form1Product.val() === 'retail bowling') {
                $Panel2Form1a.show();
                $Panel2Form1b.hide();
                $Panel2Form1c.hide();
                $Panel2Form1AfterPartyFriday.hide();
            }
            else if ( $Panel2Form1Product.val() === 'retail shoe') {
                $Panel2Form1a.hide();
                $Panel2Form1b.hide();
                $Panel2Form1c.show();
                $Panel2Form1AfterPartyFriday.hide();
            }
            else if ( $Panel2Form1Product.val() === 'after party friday') {
                $Panel2Form1a.hide();
                $Panel2Form1b.hide();
                $Panel2Form1c.hide();
                $Panel2Form1AfterPartyFriday.show();
            }
            else {
                $Panel2Form1a.hide();
                $Panel2Form1b.show();
                $Panel2Form1c.hide();
                $Panel2Form1AfterPartyFriday.hide();
            }

            // DOW change
            if ( $.inArray($Panel2Form1Product.val(), ['retail bowling', 'retail shoe']) === -1) {
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
            if (is_date || start.length === 0){
                $.get('/RM/Pricing/panel1/form1/submit', {'product': $Panel2Form1Product.val()}, function (res) {
                    var status = res['status'],
                        msg = res['msg'];
                    if (status === 1){
                        $Panel1Table1Id.bootstrapTable('destroy');
                        var columns = res['columns'];
                        PricingPanel1.Panel1Table1_init($Panel2Form1Product.val(), $Panel2Form1Start.val(),columns)
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
            $.get('/RM/Pricing/panel2/form1/submit',data,function (res) {

                clear_form();
                $.get('/RM/Pricing/panel1/form1/submit', {'product': $Panel2Form1Product.val()}, function (res) {
                    var status = res['status'],
                        msg = res['msg'];
                    if (status === 1){
                        $Panel1Table1Id.bootstrapTable('destroy');
                        var columns = res['columns'];
                        PricingPanel1.Panel1Table1_init($Panel2Form1Product.val(), null, columns)
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
                }else {
                    $Panel2Form1Submit.html("Try Again");
                    alert(msg)
                }
                timeOut = setTimeout(function() {
                    $Panel2Form1Submit.html("Submit");
                }, 2000);
            });

            return false
        });

        // Form1a change events
        $Panel2Form1NpPriceSymbol.change(function () {
            if ($Panel2Form1NpPriceSymbol.val() === 'equal') {
                $Panel2Form1NpPriceBase.prop( 'disabled', true);
                $Panel2Form1NpPriceBase.hide()
            }
            else {
                $Panel2Form1NpPriceBase.prop( 'disabled', false);
                $Panel2Form1NpPriceBase.show()

            }
        });

        $Panel2Form1PrimewkPriceSymbol.change(function () {
            if ($Panel2Form1PrimewkPriceSymbol.val() === 'equal') {
                $Panel2Form1PrimewkPriceBase.prop( 'disabled', true);
                $Panel2Form1PrimewkPriceBase.hide()
            }
            else {
                $Panel2Form1PrimewkPriceBase.prop( 'disabled', false);
                $Panel2Form1PrimewkPriceBase.show()
            }
        });

        $Panel2Form1PrimewkdPriceSymbol.change(function () {
            if ($Panel2Form1PrimewkdPriceSymbol.val() === 'equal') {
                $Panel2Form1PrimewkdPriceBase.prop( 'disabled', true);
                $Panel2Form1PrimewkdPriceBase.hide()
            }
            else {
                $Panel2Form1PrimewkdPriceBase.prop( 'disabled', false);
                $Panel2Form1PrimewkdPriceBase.show()
            }
        });

        $Panel2Form1PremiumPriceSymbol.change(function () {
            if ($Panel2Form1PremiumPriceSymbol.val() === 'equal') {
                $Panel2Form1PremiumPriceBase.prop( 'disabled', true);
                $Panel2Form1PremiumPriceBase.hide()
            }
            else {
                $Panel2Form1PremiumPriceBase.prop( 'disabled', false);
                $Panel2Form1PremiumPriceBase.show()

            }
        });

        // Form1c change events
        $Panel2Form1wkPriceSymbol.change(function () {
            if ($Panel2Form1wkPriceSymbol.val() === 'equal') {
                $Panel2Form1wkPriceBase.prop( 'disabled', true);
                $Panel2Form1wkPriceBase.hide()
            }
            else {
                $Panel2Form1wkPriceBase.prop( 'disabled', false);
                $Panel2Form1wkPriceBase.show()

            }
        });

        $Panel2Form1wkndPriceSymbol.change(function () {
            if ($Panel2Form1wkndPriceSymbol.val() === 'equal') {
                $Panel2Form1wkndPriceBase.prop( 'disabled', true);
                $Panel2Form1wkndPriceBase.hide()
            }
            else {
                $Panel2Form1wkndPriceBase.prop( 'disabled', false);
                $Panel2Form1wkndPriceBase.show()
            }
        });

        // Form1AfterPartyFriday change events
        $Panel2Form18pmPriceSymbol.change(function () {
            if ($Panel2Form18pmPriceSymbol.val() === 'equal') {
                $Panel2Form18pmPriceBase.prop( 'disabled', true);
                $Panel2Form18pmPriceBase.hide()
            }
            else {
                $Panel2Form18pmPriceBase.prop( 'disabled', false);
                $Panel2Form18pmPriceBase.show()
            }
        });

        $Panel2Form19pmPriceSymbol.change(function () {
            if ($Panel2Form19pmPriceSymbol.val() === 'equal') {
                $Panel2Form19pmPriceBase.prop( 'disabled', true);
                $Panel2Form19pmPriceBase.hide()
            }
            else {
                $Panel2Form19pmPriceBase.prop( 'disabled', false);
                $Panel2Form19pmPriceBase.show()
            }
        });

        $Panel2Form110pmPriceSymbol.change(function () {
            if ($Panel2Form110pmPriceSymbol.val() === 'equal') {
                $Panel2Form110pmPriceBase.prop( 'disabled', true);
                $Panel2Form110pmPriceBase.hide()
            }
            else {
                $Panel2Form110pmPriceBase.prop( 'disabled', false);
                $Panel2Form110pmPriceBase.show()
            }
        });

        $Panel2Form111pmPriceSymbol.change(function () {
            if ($Panel2Form111pmPriceSymbol.val() === 'equal') {
                $Panel2Form111pmPriceBase.prop( 'disabled', true);
                $Panel2Form111pmPriceBase.hide()
            }
            else {
                $Panel2Form111pmPriceBase.prop( 'disabled', false);
                $Panel2Form111pmPriceBase.show()
            }
        });
    }

    function clear_form () {
        // clear form 1
        $Panel2Form1Start.val('');
        $Panel2Form1End.val('');
        $Panel2Form1DOW.val(null).trigger('change');
        // clear form 1a
        $Panel2Form1NpPriceSymbol.val('plus');
        $Panel2Form1PrimewkPriceSymbol.val('plus');
        $Panel2Form1PrimewkdPriceSymbol.val('plus');
        $Panel2Form1PremiumPriceSymbol.val('plus');
        $Panel2Form1NpPrice.val('');
        $Panel2Form1PrimewkPrice.val('');
        $Panel2Form1PrimewkdPrice.val('');
        $Panel2Form1PremiumPrice.val('');
        $Panel2Form1NpPriceUnit.val('dollar');
        $Panel2Form1PrimewkPriceUnit.val('dollar');
        $Panel2Form1PrimewkdPriceUnit.val('dollar');
        $Panel2Form1PremiumPriceUnit.val('dollar');
        $Panel2Form1NpPriceBase.val('108');
        $Panel2Form1PrimewkPriceBase.val('110');
        $Panel2Form1PrimewkdPriceBase.val('111');
        $Panel2Form1PremiumPriceBase.val('113');

        $Panel2Form1NpPriceBase.prop( 'disabled', false);
        $Panel2Form1NpPriceBase.show();
        $Panel2Form1PrimewkPriceBase.prop( 'disabled', false);
        $Panel2Form1PrimewkPriceBase.show();
        $Panel2Form1PrimewkdPriceBase.prop( 'disabled', false);
        $Panel2Form1PrimewkdPriceBase.show();
        $Panel2Form1PremiumPriceBase.prop( 'disabled', false);
        $Panel2Form1PremiumPriceBase.show();

        // clear form 1b
        $('#price-symbol').val('plus');
        $('#price').val('');
        $('#price-unit').val('dollar');

        // clear form 1c
        $Panel2Form1wkPriceSymbol.val('plus');
        $Panel2Form1wkndPriceSymbol.val('plus');
        $Panel2Form1wkPrice.val('');
        $Panel2Form1wkndPrice.val('');
        $Panel2Form1wkPriceUnit.val('dollar');
        $Panel2Form1wkndPriceUnit.val('dollar');
        $Panel2Form1wkPriceBase.val('114');
        $Panel2Form1wkndPriceBase.val('115');

        $Panel2Form1wkPriceBase.prop( 'disabled', false);
        $Panel2Form1wkPriceBase.show();
        $Panel2Form1wkndPriceBase.prop( 'disabled', false);
        $Panel2Form1wkndPriceBase.show();

        // clear form 1AfterPartyFriday
        $Panel2Form18pmPriceSymbol.val('plus');
        $Panel2Form19pmPriceSymbol.val('plus');
        $Panel2Form110pmPriceSymbol.val('plus');
        $Panel2Form111pmPriceSymbol.val('plus');
        $Panel2Form18pmPrice.val('');
        $Panel2Form19pmPrice.val('');
        $Panel2Form110pmPrice.val('');
        $Panel2Form111pmPrice.val('');
        $Panel2Form18pmPriceUnit.val('dollar');
        $Panel2Form19pmPriceUnit.val('dollar');
        $Panel2Form110pmPriceUnit.val('dollar');
        $Panel2Form111pmPriceUnit.val('dollar');
        $Panel2Form18pmPriceBase.val('2146481686');
        $Panel2Form19pmPriceBase.val('2146532909');
        $Panel2Form110pmPriceBase.val('2146507303');
        $Panel2Form111pmPriceBase.val('2146481687');
    }

    exports.run = run;

    return exports
});
