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

    var $FileType = $('#FileType'),
        $FileUpload = $('#FileUpload'),
        $Panel1Form1Submit = $('#OpenHoursPanel1Form1Submit'),
        $Panel1Form1 = $('#OpenHoursPanel1Form1'),
        FileType = $FileType.val();

    var $Panel2Table1ContainerId = $("#OpenHoursPanel2Table1ContainerId"),
        $Panel2Table1Id = $("#OpenHoursPanel2Table1Id");

    $(function () {
        init();
        event()
    });

    function init() {

        $FileUpload.fileinput({
            uploadUrl: '/RM/OpenHours/panel1/form1/fileupload',
            maxFilePreviewSize: 10240,
            minFileCount: 1,
            // maxFileCount: 1,
            uploadAsync: false,
            browseOnZoneClick: true,
            uploadExtraData: function (previewId, index){
                return {
                    'csrfmiddlewaretoken': csrf_token,
                    'FileType':FileType
                };
            }
        });

        $Panel2Table1Id.bootstrapTable({
            // height:700,
            striped:true,
            minimumCountColumns:2,
            showFooter:false,
            pagination:true,
            paginationLoop: true,
            sidePagination: 'server',
            pageSize: 10,
            pageList: [10, 25, 50, 100, 'All'],
            showExport:true,
            exportTypes:['json', 'xml', 'csv', 'txt', 'sql', 'xlsx'],
            // filterControl:true,
            filter:true,
            url:"/RM/OpenHours/panel2/table1/create",
            columns:[
                {
                    field: 'center_id',
                    title: 'Id',
                    sortable: true,
                    editable: false,
                    align: 'center',
                    filter:{
                        type:'input'
                    }
                },
                {
                    field: 'center_name',
                    title: 'Name',
                    sortable: true,
                    editable: false,
                    align: 'center',
                    filter:{
                        type:'input'
                    }
                },
                {
                    field: 'mon',
                    title: 'Monday',
                    sortable: true,
                    editable: false,
                    align: 'center',
                },
                {
                    field: 'tue',
                    title: 'Tuesday',
                    sortable: true,
                    editable: false,
                    align: 'center',
                },
                {
                    field: 'wed',
                    title: 'Wednesday',
                    sortable: true,
                    editable: false,
                    align: 'center',
                },
                {
                    field: 'thu',
                    title: 'Thursday',
                    sortable: true,
                    editable: false,
                    align: 'center',
                },
                {
                    field: 'fri',
                    title: 'Friday',
                    sortable: true,
                    editable: false,
                    align: 'center',
                },
                {
                    field: 'sat',
                    title: 'Saturday',
                    sortable: true,
                    editable: false,
                    align: 'center',
                },
                {
                    field: 'sun',
                    title: 'Sunday',
                    sortable: true,
                    editable: false,
                    align: 'center',
                },
            ],
            rowAttributes:function (row, index) {
            },
        });
    }

    function event() {

        $Panel1Form1.submit(function (e) {

            var data = $(this).serialize();

            $Panel1Form1Submit.html("Loading...");
            $.get('/RM/OpenHours/panel1/form1/submit',data,function (res) {
                var status = res['status'],
                    msg = res['msg'];
                if (status === 1){
                    $Panel1Form1Submit.html("Loaded");
                }else {
                    $Panel1Form1Submit.html("Try Again");
                    alert(msg)
                }
            });

            return false
        });

        //editable events
        $Panel2Table1Id.on('editable-save.bs.table',function (editable, field, row, oldValue, $el) {

            row['field'] = field;

            $.get('/RM/OpenHours/panel2/table1/edit', row,function () {
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
});
