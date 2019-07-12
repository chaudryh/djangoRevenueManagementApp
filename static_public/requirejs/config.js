/**
 * Created by caliburn on 17-3-11.
 */
require.config({

    baseUrl:'static',
    paths : {
        'jquery' : ['/static/gentelella/vendors/jquery/dist/jquery.min'
                    // ,'https://ajax.googleapis.com/ajax/libs/jquery/2.2.3/jquery.min'
                    ],
        'js-cookie' : ['/static/js-cookie/src/js.cookie'],
        'bootstrap' : [
                        // 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min',
                       '/static/gentelella/vendors/bootstrap/dist/js/bootstrap.min'],
        'bootstrap-table' : ['/static/bootstrap-table/dist/bootstrap-table'],
        'bootstrap-fileinput' : ['/static/bootstrap-fileinput/js/fileinput.min'],
        'bootstrap-datepicker':['/static/bootstrap-datepicker/dist/js/bootstrap-datepicker.min'],
        'gentelella' : ['/static/gentelella/build/js/custom'],
        'select2' : [
                    // 'https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/js/select2.min',
                     '/static/select2/dist/js/select2.min'],
        'moment' : ['/static/fullcalendar-scheduler/lib/moment.min'],
        'jquery-ui' : ['/static/fullcalendar-scheduler/lib/jquery-ui.min'],
        'fullcalendar' : ['/static/fullcalendar/fullcalendar.min'],
        'scheduler' : ['/static/fullcalendar-scheduler/scheduler.min'],
        'qTip2' : ['/static/qTip2/dist/jquery.qtip.min'],
        'pnotify' : ['/static/gentelella/vendors/pnotify/dist/pnotify'],
        'pnotify-buttons' : ['/static/gentelella/vendors/pnotify/dist/pnotify.buttons'],
        'pnotify-nonblock' : ['/static/gentelella/vendors/pnotify/dist/pnotify.nonblock'],
        'pnotify-animate' : ['/static/gentelella/vendors/pnotify/dist/pnotify.animate'],
        'screenfull':['/static/screenfull/dist/screenfull.min'],
        'html2canvas': ['/static/html2canvas/dist/html2canvas'],
        // progressbar
        'nprogress' : ['/static/gentelella/vendors/nprogress/nprogress'],
        'bootstrap-progressbar' : [
            '/static/gentelella/vendors/bootstrap-progressbar/bootstrap-progressbar.min',
            // '/static/bootstrap-progressbar/bootstrap-progressbar.min'
        ],
        // bootstrap table extensions
        'bootstrap-table-export' : ['/static/requirejs/bootstrap-table/bootstrap-table-export'],
        'tableExport' : ['/static/tableExport/tableExport'],
        'FileSaver' : ['/static/tableExport/libs/FileSaver/FileSaver.min'],
        'js-xlsx' : ['/static/tableExport/libs/js-xlsx/xlsx.core.min'],
        'bootstrap-table-editable' : ['/static/bootstrap-table/dist/extensions/editable/bootstrap-table-editable.min'],
        'x-editable' : ['/static/x-editable/bootstrap3-editable/js/bootstrap-editable'],
        'filter-control' : ['/static/bootstrap-table/dist/extensions/filter-control/bootstrap-table-filter-control.min'],
        'flat-json' : ['/static/bootstrap-table/dist/extensions/flat-json/bootstrap-table-flat-json.min'],
        'multiple-sort' : ['/static/bootstrap-table/dist/extensions/multiple-sort/bootstrap-table-multiple-sort.min'],
        'select2-filter' : ['/static/bootstrap-table/dist/extensions/select2-filter/bootstrap-table-select2-filter'],
        'jquery-treegrid' : ['/static/jquery-treegrid/js/jquery.treegrid.min'],
        'bootstrap-table-treegrid': ['/static/bootstrap-table/src/extensions/treegrid/bootstrap-table-treegrid'],
        'bootstrap-table-group-by': ['/static/bootstrap-table/src/extensions/group-by-v2/bootstrap-table-group-by'],
        // Highcharts
        'Highcharts': ['/static/Highcharts/code/js/highcharts'],
        'Highcharts-more': ['/static/Highcharts/code/js/highcharts-more'],
        'Highcharts-exporting': ['/static/Highcharts/code/js/modules/exporting'],
    },
    shim:{

        'jquery':{
            exports:'jquery'
        },
        'js-cookie':{
            deps:['jquery'],
            exports:'Cookies'
        },
        'bootstrap':{
            deps:['jquery'],
            exports: 'bootstrap'
        },
        'bootstrap-table':{
            deps:['jquery','bootstrap']
        },
        'bootstrap-fileinput':{
            deps:['jquery','bootstrap']
        },
        'bootstrap-datepicker':{
            deps:['jquery','bootstrap']
        },
        'gentelella':{
            deps:['jquery','bootstrap']
        },
        'select2':{
            deps:['jquery','bootstrap']
        },
        'moment':{
            deps:[]
        },
        'jquery-ui':{
            deps:['jquery']
        },
        'fullcalendar':{
            deps:['jquery','moment']
        },
        'scheduler':{
            deps:['jquery','moment','fullcalendar']
        },
        'qTip2':{
            deps:['jquery','bootstrap']
        },
        'pnotify':{
            deps:['jquery','bootstrap']
        },
        'bootstrap-progressbar':{
            deps:['jquery','bootstrap']
        },
        'screenfull':{
            deps:['jquery','bootstrap'],
            exports: 'screenfull'
        },
        'html2canvas':{
            deps:['jquery','bootstrap'],
            exports: 'html2canvas'
        },
        // bootstrap table extensions
        'bootstrap-table-export':{
            deps:['jquery','bootstrap','bootstrap-table', 'js-xlsx', 'FileSaver', 'tableExport']
        },
        'FileSaver':{
            deps:['jquery','bootstrap']
        },
        'js-xlsx':{
            deps:['jquery','bootstrap']
        },
        'tableExport':{
            deps:['jquery','bootstrap', 'js-xlsx']
        },
        'bootstrap-table-editable':{
            deps:['jquery','bootstrap','bootstrap-table','x-editable']
        },
        'x-editable':{
            deps:['jquery','bootstrap']
        },
        'filter-control':{
            deps:['jquery','bootstrap','bootstrap-table']
        },
        'flat-json':{
            deps:['jquery','bootstrap','bootstrap-table']
        },
        'multiple-sort':{
            deps:['jquery','bootstrap','bootstrap-table']
        },
        'select2-filter':{
            deps:['jquery','bootstrap','bootstrap-table']
        },
        'jquery-treegrid':{
            deps:['jquery','bootstrap']
        },
        'bootstrap-table-treegrid':{
            deps:['jquery','bootstrap','bootstrap-table']
        },
        'bootstrap-table-group-by':{
            deps:['jquery','bootstrap','bootstrap-table']
        },
        // Highcharts
        'Highcharts':{
            deps:['jquery','bootstrap'],
            exports: 'Highcharts'
        },
        'Highcharts-more':{
            deps:['jquery','bootstrap','Highcharts'],
            exports: 'Highcharts-more'
        },
        'Highcharts-exporting':{
            deps:['jquery','bootstrap','Highcharts'],
            exports: 'Highcharts-exporting'
        }
    }
});

//global functions defined to set default settings for certain bootstrap properties
define(function (require) {
    var $ = require('jquery'),
        bootstrap = require('bootstrap'),
        datepicker = require('bootstrap-datepicker'),
        gentelella = require('gentelella'),
        select2 = require('select2');

    $(function () {
        $('.select2_single').select2({
            allowClear: true
        });
        $(".select2_multiple").select2({
          // maximumSelectionLength: 4,
          // placeholder: "With Max Selection limit 4",
          allowClear: true
        });
        $(".datepicker").datepicker({
            todayHighlight: true,
            format: "mm/dd/yy",
            // forceParse: false,
            startDate: '01/01/2010',
            assumeNearbyYear: true
        });
    });

    $.fn.serializeObject = function() {
      var o = {};
      var a = this.serializeArray();
      $.each(a, function() {
          if (o[this.name] !== undefined) {
              if (!o[this.name].push) {
                  o[this.name] = [o[this.name]];
              }
              o[this.name].push(this.value || '');
          } else {
              o[this.name] = this.value || '';
          }
      });
      return o;
    };
});

