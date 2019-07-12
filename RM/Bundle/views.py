import os
import numpy as np
import pandas as pd
import re
from datetime import datetime as dt
import pytz
import time
import json

from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
from django.views.decorators.csrf import csrf_protect, csrf_exempt

from bowlero_backend.settings import TIME_ZONE, BASE_DIR
from .models.models import *

from DAO.DataDAO import *
from DAO.DataReviseDAO import *

from utils.UString import UString
from utils.UDatetime import UDatetime

# Create your views here.
# from .utils.LoadConfigData import LoadConfigData

EST = pytz.timezone(TIME_ZONE)


@staff_member_required(login_url='/login/')
@csrf_protect
def index(request, *args, **kwargs):
    template_name = 'Bundle/BundleIndex.html'
    return render(request, template_name)

#this class isn't being used in Bundles
class Panel1:
    class Form1:

        # result_path = os.path.join(BASE_DIR, 'media/RM/Centers/centers.xlsx')

        @staticmethod
        def submit(request, *args, **kwargs):
            action = request.GET.get('action')
            date = request.GET.get('date')
            price_type = request.GET.get('price_type')
            categories = request.GET.get('categories')
            categories = categories.split(',')
            categories = [int(category) for category in categories if category]

            # data init
            if not date:
                date = UDatetime.now_local().date()
            if not price_type:
                price_type = 'regular'

            if action == 'bulk pricing':
                if not categories:
                    return JsonResponse({'status': 1, 'msg': ''})
                price_symbol = request.GET.get('price-symbol')
                price = request.GET.get('price')
                price_unit = request.GET.get('price-unit')
                start = request.GET.get('start')
                end = request.GET.get('end')
                tiers = request.GET.getlist('tiers')
                if not tiers:
                    tiers = get_tiers(date, price_type)
                if start:
                    start = UDatetime.datetime_str_init(start).date()
                else:
                    start = None
                if end:
                    end = UDatetime.datetime_str_init(end).date()
                else:
                    end = None

                price = [
                    {
                     'price_symbol': price_symbol,
                     'price_delta': UString.str2float(price),
                     'price_unit': price_unit,
                    }
                ]

                AlcoholReviseDAO.bulk_pricing(start, end, price, date, price_type, categories, tiers, request.user,
                                              tracking_id=None)

            return JsonResponse({'status': 1, 'msg': ''})

        @classmethod
        def get_food_menu(cls, request, *args, **kwargs):

            menu_list = Menu.objects \
                .filter(status='active') \
                .values_list('name', flat=True)

            result = \
                [
                    {
                        "id": menu,
                        "text": menu
                    }
                    for menu in menu_list
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

        @staticmethod
        def create_columns(request, *args, **kwargs):

            date = request.GET.get('date')
            price_type = request.GET.get('price_type')

            columns = [
                {
                    'field': 'bundle_id', 'title': 'Bundle id', 'sortable': True, 'editable': False,
                    'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}, 'visible': False
                },
                {
                    'field': 'bundle_name', 'title': 'Promotions / Package Name', 'sortable': True, 'editable': False,
                    'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                },
                {
                    'field': 'products', 'title': 'Package Components', 'sortable': True, 'editable': False,
                    'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                },
            ]

            return JsonResponse({'status': 1, 'msg': '', 'columns': columns})

        @staticmethod
        def create_details_columns(request, *args, **kwargs):

            date = request.GET.get('date')
            price_type = request.GET.get('price_type')

            columns = [
                {
                    'field': 'bundle_id', 'title': 'Bundle id', 'sortable': True, 'editable': False,
                    'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}, 'visible': False
                },
                {
                    'field': 'product_id', 'title': 'product id', 'sortable': True, 'editable': False,
                    'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}, 'visible': False
                },
                {
                    'field': 'product_num', 'title': 'Product Num', 'sortable': True, 'editable': False,
                    'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                },
                {
                    'field': 'product_name', 'title': 'Product Name', 'sortable': True, 'editable': False,
                    'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                },
            ]

            return JsonResponse({'status': 1, 'msg': '', 'columns': columns})

        @staticmethod
        def create(request, *args, **kwargs):
            page_size = int(request.GET.get('limit'))
            offset = int(request.GET.get('offset'))
            filters = request.GET.get('filter')
            sort = request.GET.get('sort')
            order = request.GET.get('order')

            data, num = BundleGet.get_bundle(
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
        def create_details(request, *args, **kwargs):
            page_size = int(request.GET.get('limit'))
            offset = int(request.GET.get('offset'))
            filters = request.GET.get('filter')
            sort = request.GET.get('sort')
            order = request.GET.get('order')
            bundle_id = request.GET.get('bundle_id')

            data, num = BundleGet.get_bundle_detail(
                                         bundle_id,
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
            category_id = request.GET.get('category_id')
            category = request.GET.get('category')
            level = request.GET.get('level')
            price_type = request.GET.get('price_type')
            date = request.GET.get('date')
            field = request.GET.get('field')
            new_value = request.GET.get(field)
            old_value = request.GET.get('old_value')

            if not date:
                date = UDatetime.now_local().date()
            if not price_type:
                price_type = 'regular'

            if field.isdigit():
                new_value = new_value.replace('$', '')
                old_value = old_value.replace('$', '')
                new_value = round(float(new_value), 2)
                old_value = round(float(old_value), 2)
                if new_value == '-':
                    new_value = None
                if old_value == '-':
                    old_value = None

                # Tracking
                # tracking_type = TrackingType.objects.get(type='retail food tier price change')
                tracking_type = None
                content_type = ContentType.objects.get_for_model(AlcoholTier)
                input_params = {'new_price': new_value, 'old_price': old_value, 'category': category, 'level': level,
                                'price_typ': price_type, 'start': str(date), 'tier': field}
                tracking_id = Tracking.objects.create(
                    username=current_user,
                    tracking_type=tracking_type,
                    content_type=content_type,
                    input_params=input_params
                )

                category_id = AlcoholCategory.objects.get(category_id=category_id)

                AlcoholTier.objects \
                    .update_or_create(
                        category_id=category_id,
                        price_type=price_type,
                        tier=field,
                        defaults={
                            'price': new_value,
                            'action_user': current_user,
                            'tracking_id': tracking_id
                        }
                    )

                # Tracking Change Report
                description = 'Change category "{category}" level "{level}" tier "{tier}" price ' \
                              'from "${price_old}" to "${price_new}"'\
                    .format(category=category, level=level, tier=field, price_old=old_value, price_new=new_value)

                AlcoholChangeReport.objects \
                    .update_or_create\
                        (
                            tracking_id=tracking_id,
                            username=current_user,
                            action_time=UDatetime.now_local(),
                            product_id=None,
                            menu=None,
                            category=category,
                            level=level,
                            tier=field,
                            description=description,
                            price_old=old_value,
                            price_new=new_value,
                            start=date,
                            end=None
                        )

            return JsonResponse({})
