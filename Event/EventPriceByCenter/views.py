import os
import numpy as np
import pandas as pd
import re
from datetime import datetime as dt
import pytz
import time

from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
from django.views.decorators.csrf import csrf_protect, csrf_exempt

from bowlero_backend.settings import TIME_ZONE, BASE_DIR

from DAO.DataDAO import *

from utils.UTable import UTable

# Create your views here.
# from .utils.LoadConfigData import LoadConfigData

EST = pytz.timezone(TIME_ZONE)


@staff_member_required(login_url='/login/')
@csrf_protect
def index(request, *args, **kwargs):
    template_name = 'EventPriceByCenter/EventPriceByCenterIndex.html'
    return render(request, template_name)


class Panel1:
    class Form1:

        # result_path = os.path.join(BASE_DIR, 'media/RM/Centers/centers.xlsx')

        @classmethod
        def submit(cls, request, *args, **kwargs):
            response = Panel2.Table1.get_columns(request=request)

            return response

        @classmethod
        def get_selections(cls, request, *args, **kwargs):
            search = request.GET.get('search')
            selectType = request.GET.get('selectType')
            groupSelections = request.GET.getlist('groupSelections[]')
            productSelections = request.GET.getlist('productSelections[]')
            centerSelections = request.GET.getlist('centerSelections[]')

            if selectType == 'groupSelections':
                seleList = EventPriceByCenter.objects.filter().values_list('group', flat=True).distinct()
                seleList = sorted(seleList)
            elif selectType == 'productSelections':
                seleList = EventPriceByCenter.objects.filter()
                if 'All' not in groupSelections and groupSelections:
                    seleList = seleList.filter(group__in=groupSelections)
                seleList = seleList.values_list('product', flat=True).distinct()
                seleList = sorted(seleList)
            elif selectType == 'centerSelections':
                seleList = EventPriceByCenter.objects.filter()
                if 'All' not in groupSelections and groupSelections:
                    seleList = seleList.filter(group__in=groupSelections)
                if 'All' not in productSelections and productSelections:
                    seleList = seleList.filter(product__in=productSelections)
                seleList = seleList.values_list('center_id', flat=True).distinct()
                seleList = [int(sel) for sel in seleList]
                seleList = sorted(seleList)
            else:
                return JsonResponse({'status': 1, 'msg': '', 'results': []})

            seleList = ['All'] + list(seleList)

            result = \
                [
                    {
                        'id': item,
                        "text": item,
                    }
                    for item in seleList
                ]

            return JsonResponse({'status': 1, 'msg': '', 'results': result})

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

        @classmethod
        def get_columns(cls, request, *args, **kwargs):
            # if not product:
            #     product = 1
            # product_obj = EventPriceByCenter.objects.filter(id=product)[0]
            # group = product_obj.group
            # product = product_obj.product

            # columns_duration = EventPriceByCenter.objects \
            #     .filter(
            #             # group=group,
            #             # product=product
            #             ) \
            #     .values_list('duration', flat=True).distinct()
            columns_duration = ['Flat rate', '30 min', '1 hour', '1.5 hours', '2 hours', '2.5 hours', '3 hours ']

            columns = \
                [
                    {
                        'field': 'center_id', 'title': 'Id', 'width':50, 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'center_name', 'title': 'Center Name', 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'territory', 'title': 'District', 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'sale_region', 'title': 'Region', 'width':70, 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'group', 'title': 'Group', 'width':50, 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'product', 'title': 'Product', 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                ]

            columns += \
                [
                    {
                        'field': column_duration,
                        'title': column_duration,
                        'editable': True,
                        'align': 'center',
                        'vlign': 'center',
                    }
                    for column_duration in columns_duration
                ]

            return JsonResponse({'status': 1, 'msg': '', 'columns': columns})

        @staticmethod
        def create(request, *args, **kwargs):
            page_size = int(request.GET.get('limit'))
            offset = int(request.GET.get('offset'))
            filters = request.GET.get('filter')
            sort = request.GET.get('sort')
            order = request.GET.get('order')

            groupSelections = request.GET.getlist('groupSelections[]')
            productSelections = request.GET.getlist('productSelections[]')
            centerSelections = request.GET.getlist('centerSelections[]')

            data, num = GetEvent.get_event_price_by_center(groupSelections, productSelections, centerSelections,
                                                           pagination=True,
                                                           page_size=page_size,
                                                           offset=offset,
                                                           filters=filters,
                                                           sort=sort,
                                                           order=order
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
        @permission_required('Models.change_eventpricebycenter', raise_exception=True)
        def edit(request, *args, **kwargs):
            # Tracking
            current_user = request.user
            center_id = request.GET.get('center_id')
            group = request.GET.get('group')
            product = request.GET.get('product')
            order = request.GET.get('order')

            field = request.GET.get('field')
            new_value = request.GET.get(field)
            old_value = request.GET.get('old_value')
            duration = field

            old_value = old_value.replace('$', '')
            new_value = new_value.replace('$', '')

            # Tracking
            tracking_type_name = 'retail bowling tier price change'
            tracking_type = TrackingType.objects.get(type=tracking_type_name)
            content_type = ContentType.objects.get_for_model(ProductPrice)
            input_params = {'price': new_value,
                            'old_value': old_value,
                            'center_id': center_id,
                            'group': group,
                            'product': product,
                            'duration': duration,
                            'order': order
                            }
            tracking_id = Tracking.objects.create(
                username=current_user,
                tracking_type=tracking_type,
                content_type=content_type,
                input_params=input_params
            )
            #

            center_id = Centers.objects.get(center_id=center_id)
            EventPriceByCenter.objects \
                .update_or_create(
                    group=group,
                    product=product,
                    center_id=center_id,
                    duration=duration,
                    defaults={
                        # 'price': new_value,
                        # Back
                        'price': new_value if new_value else None,
                        'action_user': current_user,
                        'tracking_id': tracking_id,
                        'order': order
                    }
                )

            return JsonResponse({})
