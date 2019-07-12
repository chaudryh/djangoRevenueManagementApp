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
from .models.models import *

from DAO.DataDAO import *
from DAO.DataReviseDAO import *

from utils.UDatetime import UDatetime
from utils.UString import UString

from Celery.tasks import *

# Create your views here.
# from .utils.LoadConfigData import LoadConfigData

EST = pytz.timezone(TIME_ZONE)


@staff_member_required(login_url='/login/')
@csrf_protect
def index(request, *args, **kwargs):
    template_name = 'EventPricing/EventPricingIndex.html'
    return render(request, template_name, {'event_bowling_product_tuple': ProductChoice.event_bowling_product_tuple,
                                           'event_basic_packages_product_tuple': ProductChoice.event_basic_packages_product_tuple
                                           })


class Panel1:
    class Form1:

        @classmethod
        def submit(cls, request, *args, **kwargs):
            product = request.GET.get('product')

            if product == 'event bowling' or not product:
                product_ids = ProductChoice.event_bowling_product_ids
            elif product == 'event shoe':
                product_ids = ProductChoice.event_shoe_product_ids
            elif product == 'event basic packages':
                product_ids = ProductChoice.event_basic_packages_product_ids
            else:
                product_ids = [product]

            product_objs = Product.objects.filter(product_id__in=product_ids)

            columns_product = \
                [
                    {
                        'field': product_obj.product_id, 'title': product_obj.short_product_name, 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    }
                    for product_obj in product_objs
                ]

            columns = \
                [
                    {
                        'field': 'state_', 'checkbox': True, 'align': 'center', 'vlign': 'center'
                    },
                    {
                        'field': 'center_id', 'title': 'Center Id', 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'center_name', 'title': 'Name', 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                ]

            columns += columns_product

            columns += \
                [
                    {
                        'field': 'region', 'title': 'Region', 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'district', 'title': 'District', 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'brand', 'title': 'Brand', 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'time_zone', 'title': 'Time', 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                ]

            return JsonResponse({'status': 1, 'msg': '', 'columns': columns})

    class Table1:

        @staticmethod
        def create(request, *args, **kwargs):
            page_size = request.GET.get('limit')
            offset = request.GET.get('offset')
            filters = request.GET.get('filter')
            sort = request.GET.get('sort')
            order = request.GET.get('order')
            product = request.GET.get('product')
            as_of_date = request.GET.get('as_of_date')

            try:
                as_of_date = UDatetime.datetime_str_init(as_of_date).date()
            except Exception as e:
                as_of_date = UDatetime.now_local().date()

            pagination = True

            if page_size:
                page_size = int(page_size)
            if offset:
                offset = int(offset)

            if product == 'event bowling':
                product_ids = ProductChoice.event_bowling_product_ids
            elif product == 'event shoe':
                product_ids = ProductChoice.event_shoe_product_ids
            elif product == 'event basic packages':
                product_ids = ProductChoice.event_basic_packages_product_ids
            else:
                product_ids = ProductChoice.event_bowling_product_ids

            response = DataDAO.get_centers(pagination=pagination,
                                           page_size=page_size,
                                           offset=offset,
                                           filters=filters,
                                           sort=sort,
                                           order=order,
                                           last_price=True,
                                           last_price_product_ids=product_ids,
                                           last_price_from_change=True,
                                           as_of_date=as_of_date,
                                           opt=False
                                           )
            # print(response)
            data = response[0]
            num = response[1]

            if pagination:
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
            else:
                if not data.empty:
                    data = data.where((pd.notnull(data)), '-')
                    response = data.to_dict(orient='records')
                else:
                    response = {
                        'total': 0,
                        'rows': []
                    }

            return JsonResponse(response, safe=False)


class Panel2:
    class Form1:
        @staticmethod
        def create(request, *args, **kwargs):
            template_name = 'Pricing/PricingPanel2Form1.html'
            return render(request, template_name)

        @staticmethod
        @permission_required('Pricing.change_retailbowlingprice', raise_exception=True)
        def submit(request, *args, **kwargs):
            # Tracking
            current_user = request.user

            start = request.GET.get('start')
            end = request.GET.get('end')
            product = request.GET.get('product')
            DOW = request.GET.getlist('DOW')
            centers = request.GET.get('centers')
            centers = centers.split(',')
            centers = [center.replace('*', '') for center in centers]

            start = UDatetime.datetime_str_init(start).date()
            if not end:
                end = None
            else:
                end = UDatetime.datetime_str_init(end).date()

            price = []
            if product == 'event bowling':
                for bowling_product_id in ProductChoice.event_bowling_product_ids:
                    x_price_symbol = request.GET.get('{product_id}-price-symbol'.format(product_id=bowling_product_id))
                    x_price = request.GET.get('{product_id}-price'.format(product_id=bowling_product_id))
                    x_price_unit = request.GET.get('{product_id}-price-unit'.format(product_id=bowling_product_id))
                    x_price_base = request.GET.get('{product_id}-price-base'.format(product_id=bowling_product_id))

                    price += [
                        {'product_id': bowling_product_id,
                         'price_symbol': x_price_symbol,
                         'price_delta': UString.str2float(x_price),
                         'price_unit': x_price_unit,
                         'product_id_base': x_price_base},
                    ]
            elif product == 'event shoe':
                product_id = '3101'
                price_symbol = request.GET.get('price-symbol')
                price = request.GET.get('price')
                price_unit = request.GET.get('price-unit')

                price = [
                    {'product_id': product_id,
                     'price_symbol': price_symbol,
                     'price_delta': UString.str2float(price),
                     'price_unit': price_unit,
                     'product_id_base': product_id}
                ]
            elif product == 'event basic packages':
                for product_id in ProductChoice.event_basic_packages_product_ids:
                    x_price_symbol = request.GET.get('{product_id}-price-symbol'.format(product_id=product_id))
                    x_price = request.GET.get('{product_id}-price'.format(product_id=product_id))
                    x_price_unit = request.GET.get('{product_id}-price-unit'.format(product_id=product_id))
                    x_price_base = request.GET.get('{product_id}-price-base'.format(product_id=product_id))
                    price += [
                        {'product_id': product_id,
                         'price_symbol': x_price_symbol,
                         'price_delta': UString.str2float(x_price),
                         'price_unit': x_price_unit,
                         'product_id_base': x_price_base},
                    ]

            # Tracking
            tracking_type = TrackingType.objects.get(type='bulk retail bowling price change')
            content_type = ContentType.objects.get_for_model(ProductPrice)

            # if not DOW:
            #     DOW = [dow[0] for dow in DOW_choice]

            # Tracking
            input_params = \
                {
                    'start': str(start),
                    'end': str(end),
                    'product': product,
                    'DOW': DOW,
                    'price': price,
                    'centers': centers
                }

            tracking_id = Tracking.objects.create(
                username=current_user,
                tracking_type=tracking_type,
                content_type=content_type,
                input_params=input_params
            )

            msg = ''
            if price:
                # DataReviseDAO.pricing_new4(start, end, product, DOW, price, centers, request.user,
                #                            tracking_id=tracking_id)
                bulk_price_change_task_from_price_change.delay(start, end, product, DOW, price, centers,
                                                               request.user.username,
                                                               tracking_id=tracking_id.tracking_id)
                msg = "RMS is updating your price changes. Price changes for all centers may take up to 15 mins. " \
                          "Subsequently the changes will be displayed in the 'Change Report'."

            return JsonResponse({'status': 1, 'msg': msg})


class Panel3:
    class Table1:

        @staticmethod
        def create(request, *args, **kwargs):
            page_size = int(request.GET.get('limit'))
            offset = int(request.GET.get('offset'))
            filters = request.GET.get('filter')
            sort = request.GET.get('sort')
            order = request.GET.get('order')

            data, num = DataDAO.get_price_table(pagination=True,
                                                page_size=page_size,
                                                offset=offset,
                                                filters=filters,
                                                sort=sort,
                                                order=order
                                                )

            if not data.empty:
                data_response = data.to_dict(orient='records')
                # data_response = [
                #     {'product':'bowling', 'center_id': '102', 'center_name': 'AMF Williamsburg Lanes', 'monday-non-prime':1},
                #     {'product': 'shoe', 'center_id': '102', 'center_name': 'AMF Williamsburg Lanes', 'monday-non-prime': 1},
                #     {'product': 'food', 'center_id': '102', 'center_name': 'AMF Williamsburg Lanes', 'monday-non-prime': 1},
                # ]
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
            center_id = request.GET.get('center_id')
            field = request.GET.get('field')
            new_value = request.GET.get(field)

            Centers.objects.filter(center_id__exact=center_id).update(**{field: new_value})

            return JsonResponse({})


