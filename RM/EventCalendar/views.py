import os
import numpy as np
import pandas as pd
import re
from datetime import datetime as dt, timedelta as td
import pytz
import time

from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
from django.views.decorators.csrf import csrf_protect, csrf_exempt

from bowlero_backend.settings import TIME_ZONE, BASE_DIR
from .models.models import *

from DAO.DataDAO import *

# Create your views here.
# from .utils.LoadConfigData import LoadConfigData

EST = pytz.timezone(TIME_ZONE)


@staff_member_required(login_url='/login/')
@csrf_protect
def index(request, *args, **kwargs):
    template_name = 'EventCalendar/EventCalendarIndex.html'
    return render(request, template_name)


class Panel1:
    class Calendar1:

        @classmethod
        def event(cls, request, *args, **kwargs):
            start = request.GET.get('start')
            end = request.GET.get('end')

            start = UDatetime.datetime_str_init(start)
            end = UDatetime.datetime_str_init(end)

            event_obj = Event.objects  \
                .filter(status__exact='active') \
                .exclude(
                    Q(start__gte=end) |
                    Q(end__lte=start)
                )
            if event_obj.exists():
                event_records = pd.DataFrame.from_records(event_obj.values('event_id',
                                                                           'event_name',
                                                                           'start',
                                                                           'end',
                                                                           'all_day',
                                                                           ))
                event_records.rename({'event_id': 'id',
                                      'event_name': 'title',
                                      'all_day': 'allDay'}, axis=1, inplace=True)

                for index, row in event_records.iterrows():
                    if row['allDay']:
                        event_records.at[index, 'start'] = row['start'].date()
                        if row['end']:
                            event_records.at[index, 'end'] = row['end'].date()
                        else:
                            event_records.at[index, 'end'] = row['start'].date()
            else:
                event_records = pd.DataFrame()

            response = event_records.to_dict(orient='records')

            return JsonResponse(response, safe=False)

        @classmethod
        def event_select(cls, request, *args, **kwargs):
            event_name = request.GET.get('event_name')
            all_day = request.GET.get('all_day')
            start = request.GET.get('start')
            end = request.GET.get('end')

            start = UDatetime.datetime_str_init(start)
            end = UDatetime.datetime_str_init(end)

            if all_day == 'true':
                all_day = True
            elif all_day == 'false':
                all_day = False

            Event.objects.create(event_name=event_name, start=start, end=end, all_day=all_day)

            return JsonResponse({'status': 1, 'msg': ''})

        @classmethod
        def event_update(cls, request, *args, **kwargs):
            event_id = request.GET.get('event_id')
            all_day = request.GET.get('all_day')
            start = request.GET.get('start')
            end = request.GET.get('end')

            start = UDatetime.datetime_str_init(start)
            end = UDatetime.datetime_str_init(end, start, td(days=1))

            if all_day == 'true':
                all_day = True
            elif all_day == 'false':
                all_day = False

            Event.objects \
                .filter(event_id=event_id) \
                .update(all_day=all_day,
                        start=start,
                        end=end
                        )

            return JsonResponse({'status': 1, 'msg': ''})

        @classmethod
        def event_click(cls, request, *args, **kwargs):
            commend = request.GET.get('commend')
            event_id = request.GET.get('event_id')
            all_day = request.GET.get('all_day')
            start = request.GET.get('start')
            end = request.GET.get('end')

            if commend == 'remove':
                Event.objects.filter(event_id=event_id).update(status='inactive')

            return JsonResponse({'status': 1, 'msg': ''})

