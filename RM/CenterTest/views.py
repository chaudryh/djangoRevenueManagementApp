import os
import numpy as np
import pandas as pd
import re
import json
from datetime import datetime as dt, timedelta
import pytz
import time
from io import BytesIO as io

from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
from django.views.decorators.csrf import csrf_protect, csrf_exempt

from bowlero_backend.settings import TIME_ZONE, BASE_DIR
from RM.Pricing.models.models import *
from BowlingShoe.BSChangeReport.models.models import *

from DAO.TestDAO import *

from Celery.tasks import *

from utils.UTable import UTable

# Create your views here.
# from .utils.LoadConfigData import LoadConfigData

EST = pytz.timezone(TIME_ZONE)
DEFAULT_RANGE = datetime.timedelta(days=6)


@staff_member_required(login_url='/login/')
@csrf_protect
def index(request, *args, **kwargs):
    template_name = 'CenterTest/CenterTestIndex.html'
    return render(request, template_name)


class Panel1:
    class Form1:

        @classmethod
        def get_selections(cls, request, *args, **kwargs):
            selectType = request.GET.get('selectType')
            search = request.GET.get('search')

            if not search:
                result = [
                    {
                        'id': 'all',
                        "text": 'All',
                    }
                ]
            else:
                result = []

            if selectType == 'district':
                centers = Centers.objects.filter(status='open') \
                    .exclude(district=None) \
                    .exclude(district__contains='closed')

                if search:
                    centers = centers.filter(district__contains=search)

                values = centers.values_list('district', flat=True).distinct()
                values = sorted(values)

                result += \
                    [
                        {
                            'id': value,
                            "text": value,
                        }
                        for value in values
                    ]
            elif selectType == 'region':
                centers = Centers.objects.filter(status='open') \
                    .exclude(region=None) \
                    .exclude(region__contains='closed')

                if search:
                    centers = centers.filter(region__contains=search)

                values = centers.values_list('region', flat=True).distinct()
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

        @classmethod
        def submit(cls, request, *args, **kwargs):

            return Panel2.Table1.get_columns(request, *args, **kwargs)


class Panel2:
    class Table1:

        @classmethod
        def get_columns(cls, request, *args, **kwargs):

            #add new column here
            columns = \
                [
                    {
                        'field': 'center_id', 'title': 'Id', 'width':50, 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'center_name', 'title': 'Name', 'sortable': True, 'editable': True,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'region', 'title': 'Region', 'sortable': True, 'editable': True,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'district', 'title': 'District', 'sortable': True, 'editable': True,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                ]

            return JsonResponse({'status': 1, 'msg': '', 'columns': columns})

        @staticmethod
        def create(request, *args, **kwargs):
            district = request.GET.getlist('district[]')
            region = request.GET.getlist('region[]')
            page_size = int(request.GET.get('limit'))
            offset = int(request.GET.get('offset'))
            filters = request.GET.get('filter')
            sort = request.GET.get('sort')
            order = request.GET.get('order')

            #print(district, region)
            columns = []
            response = TestDAO.get_centers(region, district, columns,
                                            pagination=True,
                                           page_size=page_size,
                                           offset=offset,
                                           filters=filters,
                                           sort=sort,
                                           order=order,
                                          )

            data = response[0]
            num = response[1]

            if not data.empty:
                data = data.where((pd.notnull(data)), '-')
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
        @permission_required('Centers.change_centers', raise_exception=True)
        def edit(request, *args, **kwargs):
            # Tracking
            current_user = request.user

            center_id = request.GET.get('center_id')
            field = request.GET.get('field')
            new_value = request.GET.get(field)

            if field == 'center_type':
                new_value = new_value.lower()
            center_id = center_id.replace('*', '')

            # Tracking
            tracking_type = TrackingType.objects.get(type='center info change')
            content_type = ContentType.objects.get_for_model(Centers)
            input_params = {field: new_value, 'center_id': center_id}
            tracking_id = Tracking.objects.create(
                username=current_user,
                tracking_type=tracking_type,
                content_type=content_type,
                input_params=input_params
            )
            #

            Centers.objects.filter(center_id__exact=center_id)\
                .update(**{
                    field: new_value,
                    'action_user': current_user,
                    'tracking_id': tracking_id
                })

            return JsonResponse({})    #converts the response to json

        @staticmethod
        def export(request, *args, **kwargs):
            district = request.GET.getlist('district[]')
            region = request.GET.getlist('region[]')
            page_size = request.GET.get('limit')
            offset = request.GET.get('offset')
            filters = request.GET.get('filter')
            sort = request.GET.get('sort')
            order = request.GET.get('order')
            file_type = request.GET.get('type')

            pagination = True

            if page_size:
                page_size = int(page_size)
            if offset:
                offset = int(offset)

            columns = [
                    'center_id',
                       'center_name',
                       'region',
                       'district',
                       ]

            data, num = TestDAO.get_centers(
                                            region,
                                            district,
                                            columns,
                                            pagination=True,
                                            page_size=page_size,
                                            offset=offset,
                                            filters=filters,
                                            sort=sort,
                                            order=order,
                                            )

            # data = data.where((pd.notnull(data)), "")
            #data.columns = map(str.capitalize, data.columns)

            if file_type == 'json':
                response = json.dumps(data.to_dict(orient='records'), ensure_ascii=False)
                response = HttpResponse(response, content_type='application/json')
                response['Content-Disposition'] = 'attachment; filename=export.json'
            elif file_type == 'csv':
                response = data.to_csv(index=False)
                response = HttpResponse(response, content_type='application/csv')
                response['Content-Disposition'] = 'attachment; filename=export.csv'
            elif file_type == 'xlsx':
                response = io()
                xlwriter = pd.ExcelWriter(response)
                data.to_excel(xlwriter, index=False)

                xlwriter.save()
                xlwriter.close()
                response.seek(0)

                response = HttpResponse(response.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = 'attachment; filename=export.xlsx'
            else:
                response = json.dumps([], ensure_ascii=False)
                response = HttpResponse(response, content_type='application/json')
                response['Content-Disposition'] = 'attachment; filename=export.json'

            return response

class Panel3:
    class Form1:

        @staticmethod
        @permission_required('Pricing.change_retailbowlingprice', raise_exception=False)
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
