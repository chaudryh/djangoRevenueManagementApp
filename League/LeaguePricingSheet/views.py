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
from DAO.LeagueDataDAO import *

from utils.UTable import UTable

# Create your views here.
# from .utils.LoadConfigData import LoadConfigData

EST = pytz.timezone(TIME_ZONE)


@staff_member_required(login_url='/login/')
@csrf_protect
def index(request, *args, **kwargs):
    template_name = 'LeaguePricingSheet/LeaguePricingSheetIndex.html'
    return render(request, template_name)


class Panel1:
    class Form1:

        # result_path = os.path.join(BASE_DIR, 'media/RM/Centers/centers.xlsx')

        @classmethod
        def submit(cls, request, *args, **kwargs):
            start = request.GET.get('start')
            end = request.GET.get('end')
            eff_start = request.GET.get('eff_start')
            eff_end = request.GET.get('eff_end')

            # start = UDatetime.datetime_str_init(start, timedelta(days=-30))
            # end = UDatetime.datetime_str_init(end) + timedelta(days=1)

            columns = \
                [
                    {
                        'field': 'center_id', 'title': 'Center', 'width': 200, 'sortable': False, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'center_name', 'title': 'Center Name', 'width': 200, 'sortable': False, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'region', 'title': 'Region', 'width': 200, 'sortable': False, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'district', 'title': 'District', 'width': 200, 'sortable': False, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'min_lineage_fee_bowlero', 'title': 'Min Lineage Fee Bowlero', 'width': 200, 'sortable': False, 'editable': True,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'max_lineage_fee_bowlero', 'title': 'Max Lineage Fee Bowlero', 'width': 200, 'sortable': False, 'editable': True,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'cost_of_acquisition', 'title': 'Acquisition Cost Per Bowler', 'width': 200, 'sortable': False, 'editable': True,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'cost_of_retention', 'title': 'Retention Cost Per Bowler', 'width': 200, 'sortable': False, 'editable': True,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                ]

            return JsonResponse({'status': 1, 'msg': '', 'columns': columns})

        @classmethod
        def fileupload(cls, request, *args, **kwargs):
            files = request.FILES.getlist('FileUpload')

            file_path = os.path.join(BASE_DIR, 'media/RM/Centers/centers.xlsx')

            if request.method == 'POST' and files:
                for file in files:
                    data = pd.read_excel(file)
                    data.to_excel(file_path)

            return JsonResponse({})


class Panel2:
    class Table1:

        @staticmethod
        def create(request, *args, **kwargs):
            page_size = int(request.GET.get('limit'))
            offset = int(request.GET.get('offset'))
            filters = request.GET.get('filter')
            sort = request.GET.get('sort')
            order = request.GET.get('order')
            duration = request.GET.get('duration')

            data, num = LeagueDataDao.get_league_pricing_sheet(
                                         duration=duration,
                                         pagination=True,
                                         page_size=page_size,
                                         offset=offset,
                                         filters=filters,
                                         sort=sort,
                                         order=order,
                                         )

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
        def edit(request, *args, **kwargs):
            field = request.GET.get('field')
            new_value = request.GET.get(field)
            old_value = request.GET.get('old_value')
            duration = request.GET.get('duration')
            center_id = request.GET.get('center_id')

            old_value = old_value.replace('$', '')
            new_value = new_value.replace('$', '')
            if not new_value:
                new_value = None

            numFields = ['min_lineage_fee_bowlero', 'max_lineage_fee_bowlero', 'max_cover', 'cost_of_acquisition',
                         'max_ceiling_customer_fund', 'actualPF']

            if field in numFields and new_value:
                try:
                    new_value = float(new_value)
                except:
                    return JsonResponse({})

            centerObj = Centers.objects.get(center_id=center_id)
            LeaguePricingSheet.objects \
                .update_or_create(
                    duration=duration,
                    center_id=centerObj,
                    defaults={field: new_value}
                )

            return JsonResponse({})

    class Modal1:

        @staticmethod
        def add(request, *args, **kwargs):
            current_user = request.user

            duration = request.GET.get('duration')
            center_id = request.GET.get('center_id')
            center_obj = Centers.objects.get(center_id=center_id)

            # add to League
            LeaguePricingSheet.objects.create(
                **{
                    'center_id': center_obj,
                    'duration': duration,
                    'action_user': current_user,
                    'action_time': UDatetime.now_local()
                }
            )

            return JsonResponse({'status': 1, 'msg': ''})
