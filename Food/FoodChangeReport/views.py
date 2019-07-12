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

from utils.UTable import UTable

# Create your views here.
# from .utils.LoadConfigData import LoadConfigData

EST = pytz.timezone(TIME_ZONE)


@staff_member_required(login_url='/login/')
@csrf_protect
def index(request, *args, **kwargs):
    template_name = 'FoodChangeReport/FoodChangeReportIndex.html'
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
                        'field': 'center_id', 'title': 'Center', 'width': 600, 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'product', 'title': 'Food', 'width': 600, 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'menu', 'title': 'Menu', 'width': 600, 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'tier', 'title': 'Tier', 'width': 600, 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'prod_num', 'title': 'Prod Num', 'width': 600, 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'category', 'title': 'Category', 'width': 600, 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'action_time', 'title': 'Date Time', 'width': 500, 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'username', 'title': 'User', 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'price_old', 'title': 'Old Price', 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'price_new', 'title': 'New Price', 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'product_start', 'title': 'Start', 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'product_end', 'title': 'End', 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'description', 'title': 'Change Detail', 'width': 600, 'sortable': True,
                        'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'tracking_id', 'title': 'TRXN', 'width': 75, 'sortable': True, 'editable': False,
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
            start = request.GET.get('start')
            end = request.GET.get('end')
            eff_start = request.GET.get('eff_start')
            eff_end = request.GET.get('eff_end')

            if start:
                start = dt.strptime(start, '%Y-%m-%d').date()
            if end:
                end = dt.strptime(end, '%Y-%m-%d').date() + timedelta(days=1)
            if eff_start:
                eff_start = dt.strptime(eff_start, '%Y-%m-%d').date()
            if eff_end:
                eff_end = dt.strptime(eff_end, '%Y-%m-%d').date() + timedelta(days=1)

            if not start and not end and not eff_start and not eff_end:
                start = UDatetime.datetime_str_init(start, default_delta=timedelta(days=-30)).date()
                end = UDatetime.datetime_str_init(end) + timedelta(days=1)

            data, num = DataDAO.get_food_change_report(
                                         start=start,
                                         end=end,
                                         eff_start=eff_start,
                                         eff_end=eff_end,
                                         pagination=True,
                                         page_size=page_size,
                                         offset=offset,
                                         filters=filters,
                                         sort=sort,
                                         order=order,
                                         )

            if not data.empty:
                data = data.where((pd.notnull(data)), None)

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
            food = request.GET.get('food')
            menu = request.GET.get('menu')
            category = request.GET.get('category')
            field = request.GET.get('field')
            new_value = request.GET.get(field)
            old_value = request.GET.get('old_value')

            if 'tier' in field:
                FoodMenuTable.objects \
                    .filter(product__product_name=food, menu=menu, category=category, tier=field) \
                    .update(**{'price': new_value})
            elif field == 'food':
                Product.objects \
                    .filter(product_name=old_value) \
                    .update(**{'product_name': new_value})
            elif field == 'category':
                FoodMenuTable.objects \
                    .filter(product__product_name=food, menu=menu, category=old_value) \
                    .update(**{field: new_value})
            # elif field == 'menu':
            #     Menu.objects \
            #         .filter(name=old_value) \
            #         .update(**{'name': new_value})

            return JsonResponse({})





