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

    var exports = {};
    var timeOut;

    var $Panel3Form1 = $('#ProductOptPanel3Form1'),
        $Panel3Form1Submit = $('#ProductOptPanel3Form1Submit'),
        $FileUpload = $('#FileUpload');

    var $start = $("#start"),
        $end = $('#end');


    function run () {
        init();
        event();
        // PricingTablePanel1.Panel1Table1_init();
    }

    function init() {
        $("#date").datepicker("setDate", new Date());
        // $("#DOW").select2({
        //     placeholder: "Default to all if leave empty"
        // });
        //
        // $("#product").select2({
        //     allowClear: false
        // });
        $FileUpload.fileinput({
            // uploadUrl: '/RM/ProductOpt/panel3/form1/fileupload',
            maxFilePreviewSize: 10240,
            // minFileCount: 1,
            maxFileCount: 1,
            // uploadAsync: false,
            showUpload: false,
            browseOnZoneClick: true,
            uploadExtraData: function (previewId, index){
                return {
                    'csrfmiddlewaretoken': csrf_token,
                };
            }
        });
    }

    function event() {

        $Panel3Form1.submit(function (e) {

            var formData = new FormData($Panel3Form1[0]);

            clearTimeout(timeOut);

            $Panel3Form1Submit.html("Uploading...");
            $.ajax({
                url: '/RM/ProductOpt/panel3/form1/submit',
                data: formData,
                type: 'POST',
                contentType: false,
                processData: false,
                success: function(res) {
                    var status = res['status'],
                        msg = res['msg'];
                    if (status === 1){
                        $Panel3Form1Submit.html("Processed");
                        if (msg !== '') {
                            alert(msg)
                        }
                    }else {
                        $Panel3Form1Submit.html("Try Again");
                        alert(msg)
                    }
                    timeOut = setTimeout(function() {
                        $Panel3Form1Submit.html("Submit");
                    }, 2000);
                },
                error: function() {
                    $Panel3Form1Submit.html("Try Again");
                    alert(msg)
                }
            });
            // $.post('/RM/ProductOpt/panel3/form1/submit',formData,function (res) {
            //     var status = res['status'],
            //         msg = res['msg'];
            //     if (status === 1){
            //         $Panel3Form1Submit.html("Refreshed");
            //         timeOut = setTimeout(function() {
            //             $Panel3Form1Submit.html("Submit");
            //         }, 2000);
            //     }else {
            //         $Panel3Form1Submit.html("Try Again");
            //         alert(msg)
            //     }
            // });

            return false
        });
    }

    exports.run = run;

    return exports
});
