import os
from io import BytesIO as io
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
from django.db.models import Q, Count, Min, Max, Sum, Avg

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
from django.views.decorators.csrf import csrf_protect, csrf_exempt

from bowlero_backend.settings import TIME_ZONE, BASE_DIR
from Food.FoodByCenter.models.models import *

from DAO.FoodDAO import FoodDataDao
from utils.UDatetime import UDatetime

from Celery.tasks import *

# Create your views here.
# from .utils.LoadConfigData import LoadConfigData

EST = pytz.timezone(TIME_ZONE)


@staff_member_required(login_url='/login/')
@csrf_protect
def index(request, *args, **kwargs):
    template_name = 'FoodByCenter/FoodByCenterIndex.html'
    return render(request, template_name)


class Panel1:
    class Form1:

        @classmethod
        def submit(cls, request, *args, **kwargs):

            price = request.GET.get('price')
            category_products = request.GET.getlist('category_products')

            if price and category_products and category_products != ['undefined---undefined']:
                menu_id = request.GET.get('menu_id')
                category = request.GET.get('category')
                start = request.GET.get('start')
                end = request.GET.get('end')
                priceSymbol = request.GET.get('price-symbol')
                priceUnit = request.GET.get('price-unit')
                price_ = request.GET.get('price')

                start = UDatetime.datetime_str_init(start).date() if start else UDatetime.now_local().date()
                end = UDatetime.datetime_str_init(end).date() if end else None

                category_products = [category_product.split('---') for category_product in category_products]
                category_products = [(category, product_id) for category, product_id in category_products]
                centers = Panel2.Table1.get_columns(request, centersOnly=True, *args, **kwargs)
                price = {'price_symbol': priceSymbol, 'price': float(price_), 'unit': priceUnit}

                # Get Menu
                menu = Menu.objects.filter(menu_id=menu_id)
                if menu.exists():
                    menu_name = menu[0].menu_name
                else:
                    menu_name = None

                # Tracking
                tracking_type = TrackingType.objects.get(type='retail food tier price change')
                content_type = ContentType.objects.get_for_model(FoodPrice)
                input_params = \
                    {
                        'start': str(start),
                        'end': str(end),
                        'menu_id': menu_id,
                        'menu_name': menu_name,
                        'category_products': category_products,
                        'price': price,
                        'centers': centers
                    }
                tracking_id = Tracking.objects.create(
                    username=request.user,
                    tracking_type=tracking_type,
                    content_type=content_type,
                    input_params=input_params
                )
                #

                update_food_price.delay(menu_id, category_products, centers, start, end, price, category, request.user.username, tracking_id.tracking_id)
                # FoodDataDao.updateFoodPrice(menu_id, category_products, centers, start, end, price, category, request.user, tracking_id.tracking_id)

            response = Panel2.Table1.get_columns(request, *args, **kwargs)
            return response

        @classmethod
        def get_selections(cls, request, *args, **kwargs):
            selectType = request.GET.get('selectType')
            search = request.GET.get('search')
            menuId = request.GET.get('menu_id')
            start = request.GET.get('start')

            start = UDatetime.datetime_str_init(start).date() if start else UDatetime.now_local().date()

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
            elif selectType == 'center_id':
                centers = Centers.objects.filter(status='open')

                if search:
                    if search.isdigit():
                        centers = centers.filter(center_id__contains=search)
                    else:
                        centers = centers.filter(center_name__contains=search)

                centers = centers \
                    .order_by('center_id') \
                    .extra(select={'center_id': 'CAST(center_id AS INTEGER)'})

                center_records = pd.DataFrame.from_records(centers.values('center_id',
                                                                          'center_name',
                                                                          ))
                result += \
                    [
                        {
                            'id': row['center_id'],
                            "text": str(row['center_id']) + '-' + str(row['center_name']),
                        }
                        for index, row in center_records.iterrows()
                    ]
            elif selectType == 'menu_id':
                menus = Menu.objects.filter(status='active')

                if search:
                    menus = menus.filter(menu_name__contains=search)

                menu_records = pd.DataFrame.from_records(menus.values('menu_id',
                                                                      'menu_name',
                                                                      ))
                if not menu_records.empty:
                    menu_records.sort_values(['menu_name'], inplace=True)

                result = []

                result += \
                    [
                        {
                            'id': row['menu_id'],
                            "text": row['menu_name'],
                        }
                        for index, row in menu_records.iterrows()
                    ]
            elif selectType == 'category':
                if menuId:
                    values = FoodPrice.objects \
                        .filter(menu_id=menuId) \
                        .exclude(Q(start__gt=start) |
                                 Q(end__lt=start)
                                 )

                    if search:
                        values = values.filter(category__contains=search)

                    values = values \
                        .values_list('category', flat=True) \
                        .distinct()
                else:
                    values = []

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
        def get_columns(cls, request, centersOnly=False, *args, **kwargs):
            menuId = request.GET.get('menu_id')
            category = request.GET.get('category')
            start = request.GET.get('start')
            # Get all selection values
            district = request.GET.getlist('district')
            region = request.GET.getlist('region')
            center_id = request.GET.getlist('center_id')

            # Find if all in the selections
            if district and 'all' in district:
                district = []
            if region and 'all' in region:
                region = []
            if center_id and 'all' in center_id:
                center_id = []

            # Remove empty string
            district = [item for item in district if item]
            region = [item for item in region if item]
            center_id = [item for item in center_id if item]

            # Filter centers
            centers = Centers.objects \
                .filter(status='open')

            if district:
                centers = centers.filter(district__in=district)
            if region:
                centers = centers.filter(region__in=region)
            if center_id:
                centers = centers.filter(center_id__in=center_id)

            center_list = centers.values_list('center_id', flat=True)

            start = UDatetime.datetime_str_init(start).date() if start else UDatetime.now_local().date()
            centers = FoodPrice.objects \
                .filter(status='active',
                        menu__menu_id=menuId,
                        center_id__in=center_list
                        ) \
                .exclude(Q(start__gt=start) |
                         Q(end__lt=start)
                         ) \
                .values_list('center_id', flat=True).distinct()

            centers = sorted([int(center) for center in centers])
            if centersOnly:
                return centers

            columns = \
                [
                    {
                        'field': 'state', 'title': 'State', 'checkbox': True
                    },
                    {
                        'field': 'menu', 'title': 'Menu', 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center'
                    },
                    {
                        'field': 'category', 'title': 'Category', 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center'
                    },
                    {
                        'field': 'food', 'title': 'Food', 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'product_num', 'title': 'Prod Num', 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    # {
                    #     'field': 'start', 'title': 'Start', 'sortable': True, 'editable': True,
                    #     'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    # },
                    # {
                    #     'field': 'end', 'title': 'End', 'sortable': True, 'editable': True,
                    #     'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    # },
                    {
                        'field': 'product_id', 'title': 'product_id', 'visible': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'menu_id', 'title': 'menu_id', 'visible': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                ]

            columns += [
                {
                    'field': centerId,
                    'title': centerId,
                    'editable': True,
                    'align': 'center',
                    'vlign': 'center',
                }
                for centerId in centers
            ]

            return JsonResponse({'status': 1, 'msg': '', 'columns': columns})

        @staticmethod
        def create(request, *args, **kwargs):
            page_size = int(request.GET.get('limit'))
            offset = int(request.GET.get('offset'))
            filters = request.GET.get('filter')
            sort = request.GET.get('sort')
            order = request.GET.get('order')
            start = request.GET.get('start')
            end = request.GET.get('end')
            menu_id = request.GET.get('menu_id')

            # Get all selection values (used specifically in Center selection)
            category = request.GET.getlist('category')
            district = request.GET.getlist('district')
            region = request.GET.getlist('region')
            center_id = request.GET.getlist('center_id')

            # Find if all in the selections
            if category and 'all' in category:
                category = []
            if district and 'all' in district:
                district = []
            if region and 'all' in region:
                region = []
            if center_id and 'all' in center_id:
                center_id = []

            # Remove empty string
            category = [item for item in category if item]
            district = [item for item in district if item]
            region = [item for item in region if item]
            center_id = [item for item in center_id if item]

            start = UDatetime.datetime_str_init(start).date() if start else UDatetime.now_local().date()

            data, num = FoodDataDao.getFoodByCenter(
                menu_id, start, category, district, region, center_id,
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
        @permission_required('Food.change_foodmenutable', raise_exception=True)
        def edit(request, *args, **kwargs):

            current_user = request.user
            product_id = request.GET.get('product_id')
            menu_id = request.GET.get('menu_id')
            category = request.GET.get('category')
            field = request.GET.get('field')
            new_value = request.GET.get(field)
            old_value = request.GET.get('old_value')
            start = request.GET.get('start')
            end = request.GET.get('end')
            center_id = field

            start = UDatetime.datetime_str_init(start).date() if start else UDatetime.now_local().date()
            end = UDatetime.datetime_str_init(end).date() if end else None

            price = {'price_symbol': 'equal', 'price': float(new_value), 'unit': 'dollar'}
            category_products = [(category, product_id)]
            centers = [center_id]

            # Get Menu
            menu = Menu.objects.filter(menu_id=menu_id) #get (as opposed to filter) throws an error if multiple records are returned
            if menu.exists():
                menu_name = menu[0].menu_name
            else:
                menu_name = None

            # Tracking
            tracking_type = TrackingType.objects.get(type='retail food tier price change')
            content_type = ContentType.objects.get_for_model(FoodPrice)
            input_params = \
                {
                    'start': str(start),
                    'end': str(end),
                    'menu_id': menu_id,
                    'menu_name': menu_name,
                    'category_products': category_products,
                    'price': price,
                    'centers': centers
                }
            tracking_id = Tracking.objects.create(
                username=request.user,
                tracking_type=tracking_type,
                content_type=content_type,
                input_params=input_params
            )
            #
            FoodDataDao.updateFoodPrice(menu_id, category_products, centers, start, end, price, [category], request.user, tracking_id.tracking_id)

            return JsonResponse({'status': 1, 'msg': ''})

        @staticmethod
        def export(request, *args, **kwargs):
            page_size = int(request.GET.get('limit'))
            offset = int(request.GET.get('offset'))
            filters = request.GET.get('filter')
            sort = request.GET.get('sort')
            order = request.GET.get('order')
            start = request.GET.get('start')
            end = request.GET.get('end')
            menu_id = request.GET.get('menu_id')
            file_type = request.GET.get('type')

            # Get all selection values
            category = request.GET.getlist('category')
            district = request.GET.getlist('district')
            region = request.GET.getlist('region')
            center_id = request.GET.getlist('center_id')

            # Find if all in the selections
            if category and 'all' in category:
                category = []
            if district and 'all' in district:
                district = []
            if region and 'all' in region:
                region = []
            if center_id and 'all' in center_id:
                center_id = []

            # Remove empty string
            category = [item for item in category if item]
            district = [item for item in district if item]
            region = [item for item in region if item]
            center_id = [item for item in center_id if item]

            start = UDatetime.datetime_str_init(start).date() if start else UDatetime.now_local().date()

            data, num = FoodDataDao.getFoodByCenter(
                menu_id, start, category, district, region, center_id,
                pagination=True,
                page_size=page_size,
                offset=offset,
                filters=filters,
                sort=sort,
                order=order,
                download=True
            )

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
