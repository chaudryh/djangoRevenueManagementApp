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
        fullcalendar = require('fullcalendar'),
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
        select2_filter = require('select2-filter');

    var $Panel1Calendar1 = $('#EventCalendarPanel1Calendar1');
	var	eventData_global = {};

    $(function () {
        init();
        event()
    });

    function init() {
        $Panel1Calendar1.fullCalendar({
            header: {
                left: 'prev,next today',
                center: 'title',
                right: 'month,agendaWeek,agendaDay'
            },
            height: 600,
            themeSystem: 'bootstrap4',
            lazyFetching: false,
            navLinks: true,
            editable: true,
            eventLimit: true,
            selectable: true,
            selectHelper: true,
            events: { // you can also specify a plain string like 'json/events.json'
				url: '/RM/EventCalendar/panel1/calendar1/event/',
				error: function() {}
			},
            select: function( start, end, jsEvent, view, resource) {

            	eventData_global = {
					'start': start.format(),
					'end': end.format()
				};

            	$('#EventCalendarPanel1Calendar1EventSelectCreate').click();

				return false;
			},
			eventResize: function(event, delta, revertFunc) {

				var eventData = {
					'event_id': event.id,
					'all_day': event.allDay,
					'start': event.start.format(),
					'end': event.end.format()
				};

				$.get('/RM/EventCalendar/panel1/calendar1/event_update/',eventData,function () {
                });
			},
			eventDrop: function(event, delta) { // called when an event (already on the calendar) is moved
                var end;
                if (event['end'] === null) {
                    end = null
                } else {
                    end = event.end.format()
                }

				var eventData = {
					'event_id': event.id,
					'all_day': event.allDay,
					'start': event.start.format(),
					'end': end
				};

                $.get('/RM/EventCalendar/panel1/calendar1/event_update/',eventData,function () {
                });
            },
            eventClick:function(event, jsEvent, view){
            	eventData_global = {
					'event_id': event.id,
					'all_day': event.allDay,
					'start': event.start.format(),
					'end': event.end.format()
				};

				$('#EventCalendarPanel1Calendar1EventClickCreate').click();

				return false;
			},
        })
    }

    function event() {
        $('#EventCalendarPanel1Calendar1EventClickFormId').submit(function (e) {
            var form_inputs = $(this).serializeObject();
            var data = $.extend(form_inputs, eventData_global);
            // console.log(form_inputs)

            $.get('/RM/EventCalendar/panel1/calendar1/event_click/', data,function () {
                $Panel1Calendar1.fullCalendar('refetchEvents');
                $('#EventCalendarPanel1Calendar1EventClickNo').click();
                eventData_global = {};
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

        $('#EventCalendarPanel1Calendar1EventSelectFormId').submit(function (e) {
            var form_inputs = $(this).serializeObject();
            var data = $.extend(form_inputs, eventData_global);

            $.get('/RM/EventCalendar/panel1/calendar1/event_select/', data,function () {
                $Panel1Calendar1.fullCalendar('refetchEvents');
                $('#EventCalendarPanel1Calendar1EventSelectNo').click();
                eventData_global = {};
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
});
