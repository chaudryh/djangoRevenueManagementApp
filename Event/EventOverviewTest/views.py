import os
import numpy as np
import pandas as pd
import re
from datetime import datetime as dt, timedelta
import pytz
import time

from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse

from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_protect, csrf_exempt

from bowlero_backend.settings import TIME_ZONE, BASE_DIR
from .models.models import *

from DAO.DataDAO import *
from DAO.TestDAO import *

from Celery.tasks import *

from utils.UTable import UTable

# Create your views here.
# from .utils.LoadConfigData import LoadConfigData

EST = pytz.timezone(TIME_ZONE)


@staff_member_required(login_url='/login/')
@csrf_protect
def index(request, *args, **kwargs):
    template_name = 'EventOverviewTest/EventOverviewTestIndex.html'
    return render(request, template_name)


class Panel1:
    class Form1:
        @classmethod
        def get_selections(cls, request, *args, **kwargs):
            selectType = request.GET.get('selectType')
            search = request.GET.get('search')
            #print(selectType)
            if not search:
                result = [
                    {
                        'id': 'all',
                        "text": 'All',
                    }
                ]
            else:
                result = []

            if selectType == 'sale_region':
                centers = Centers.objects.filter(status='open') \
                    .exclude(sale_region=None) \
                    .exclude(district__contains='closed')

                if search:
                    centers = centers.filter(sale_region__contains=search)

                values = centers.values_list('sale_region', flat=True).distinct()
                values = sorted(values)

                result += \
                    [
                        {
                            'id': value,
                            "text": value,
                        }
                        for value in values
                    ]
            elif selectType == 'territory':
                centers = Centers.objects.filter(status='open') \
                    .exclude(territory=None) \
                    .exclude(status__contains='closed')

                if search:
                    centers = centers.filter(territory__contains=search)

                values = centers.values_list('territory', flat=True).distinct()
                values = sorted(values)

                result += \
                    [
                        {
                            'id': value,
                            "text": value,
                        }
                        for value in values
                    ]

            return JsonResponse({'status': 1, 'msg': '', 'results': result})

            # result_path = os.path.join(BASE_DIR, 'media/RM/Centers/centers.xlsx')

        @classmethod
        def submit(cls, request, *args, **kwargs):

            columns = \
                [
                    {
                        'field': 'center_id', 'title': 'Center Id', 'width': 200, 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'center_name', 'title': 'Center Name', 'width': 200, 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'status', 'title': 'Status', 'width': 200, 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type':'select', 'data': ['open', 'closed']}
                    },
                    {
                        'field': 'sale_region', 'title': 'Sale Region', 'width': 200, 'sortable': True, 'editable': True,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'territory', 'title': 'Territory', 'width': 200, 'sortable': True, 'editable': True,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'arcade_type', 'title': 'Arcade Type', 'width': 200, 'sortable': True, 'editable': True,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'center_type', 'title': 'Center Type', 'width': 200, 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                ]

            return JsonResponse({'status': 1, 'msg': '', 'columns': columns})
            #return Panel2.Table1.get_columns(request, *args, **kwargs)


        @classmethod
        def fileupload(cls, request, *args, **kwargs):
            files = request.FILES.getlist('FileUpload')

            file_path = os.path.join(BASE_DIR, 'media/RM/Centers/centers.xlsx')

            if request.method == 'POST' and files:
                for file in files:
                    data = pd.read_excel(file)
                    data.to_excel(file_path)

            return JsonResponse({})

#static methods don't need class decorators'
class Panel2:
    class Table1:

        @staticmethod
        def create(request, *args, **kwargs):
            territory = request.GET.getlist('territory[]')
            sale_region = request.GET.getlist('sale_region[]')
            page_size = int(request.GET.get('limit'))
            offset = int(request.GET.get('offset'))
            filters = request.GET.get('filter')
            sort = request.GET.get('sort')
            order = request.GET.get('order')

            #print(sale_region, territory)

            #columns=[]
            data, num = GetEvent.get_event_overview(sale_region, territory,
                                         pagination=True,
                                         page_size=page_size,
                                         offset=offset,
                                         filters=filters,
                                         sort=sort,
                                         order=order,
                                         )

            if not data.empty:
                data = data.where((pd.notnull(data)), "-")

                data_response = data.to_dict(orient='records')
                response = {
                    'total': num,
                    'rows': data_response
                }
            else:
                response = {
                    'total': 0,
                    'rows': []
                }
            return JsonResponse(response, safe=False)

        @staticmethod
        def edit(request, *args, **kwargs):
            current_user = request.user

            center_id = request.GET.get('center_id')
            field = request.GET.get('field')
            new_value = request.GET.get(field)
            old_value = request.GET.get('old_value')

            # Remove * from session centers
            center_id = center_id.replace('*', '')

            # Tracking
            tracking_type = TrackingType.objects.get(type='event change')
            content_type = ContentType.objects.get_for_model(Centers)
            input_params = {'center_id': center_id, 'field': field, 'new_value': new_value, 'old_value': old_value}
            tracking_id = Tracking.objects.create(
                username=current_user,
                tracking_type=tracking_type,
                content_type=content_type,
                input_params=input_params
            )
            #

            Centers.objects \
                .filter(center_id=center_id) \
                .update(**{field: new_value})

            return JsonResponse({})
class Panel3:
    class Form1:

        @staticmethod
        #@permission_required('Pricing.change_retailbowlingprice', raise_exception=False)
        def submit(request, *args, **kwargs):
            #data received from the form in the panel
            current_user = request.user

            try:
                file = request.FILES.getlist('FileUpload')[0]
            except Exception as e:
                return JsonResponse({'status': 0, 'msg': 'No attached file'})

            try:
                data = pd.read_excel(file)
                data = pd.melt(data,
                               id_vars=['center_id'],
                               var_name='Sort by',
                               value_name='value'
                               )

                bulk_update_test.delay(data.to_dict())

                msg = "RMS is updating your opt changes. Opt changes for all centers may take up to 15 mins. " \
                      "Subsequently the changes will be displayed in the 'Change Report'."
            except Exception as e:
                msg = "File is not able to be parsed and processed. Make sure your file format is correct."
                return JsonResponse({'status': 0, 'msg': msg})

            return JsonResponse({'status': 1, 'msg': msg})
