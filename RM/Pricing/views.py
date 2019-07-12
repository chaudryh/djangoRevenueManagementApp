import os
import numpy as np
import pandas as pd
import re
import json
from datetime import datetime as dt
import pytz
import time
from io import BytesIO as io

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
    template_name = 'Pricing/PricingIndex.html'
    return render(request, template_name)


class Panel1:
    class Form1:

        @classmethod
        def submit(cls, request, *args, **kwargs):
            product = request.GET.get('product')

            if product == 'retail bowling' or not product:
                product_ids = ['108', '110', '111', '113']
            elif product == 'retail shoe':
                product_ids = ProductChoice.retail_shoe_product_ids_new
            elif product == 'after party friday':
                product_ids = ['2146481686', '2146532909', '2146507303', '2146481687']
            else:
                product_ids = [product]

            product_objs = Product.objects.filter(product_id__in=product_ids).order_by('order')

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

            as_of_date = UDatetime.datetime_str_init(as_of_date).date()

            pagination = True

            if page_size:
                page_size = int(page_size)
            if offset:
                offset = int(offset)

            if product == 'retail bowling':
                product_ids = ProductChoice.retail_bowling_ids_new_short
                last_price_from_change = True
            elif product == 'retail shoe':
                product_ids = ProductChoice.retail_shoe_product_ids_new
                last_price_from_change = True
            elif product == 'after party friday':
                product_ids = ['2146481686', '2146532909', '2146507303', '2146481687']
                last_price_from_change = True
            elif product:
                product_ids = [product]
                last_price_from_change = True
            else:
                product_ids = ProductChoice.retail_bowling_ids_new_short
                last_price_from_change = True

            response = DataDAO.get_centers(pagination=pagination,
                                           page_size=page_size,
                                           offset=offset,
                                           filters=filters,
                                           sort=sort,
                                           order=order,
                                           last_price=True,
                                           last_price_product_ids=product_ids,
                                           last_price_from_change=last_price_from_change,
                                           as_of_date=as_of_date
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

        @staticmethod
        def export(request, *args, **kwargs):
            page_size = request.GET.get('limit')
            offset = request.GET.get('offset')
            filters = request.GET.get('filter')
            sort = request.GET.get('sort')
            order = request.GET.get('order')
            product = request.GET.get('product')
            as_of_date = request.GET.get('as_of_date')
            file_type = request.GET.get('type')

            as_of_date = UDatetime.datetime_str_init(as_of_date).date()
            pagination = True

            if page_size:
                page_size = int(page_size)
            if offset:
                offset = int(offset)

            if product == 'retail bowling':
                product_ids = ProductChoice.retail_bowling_ids_new_short
            elif product == 'retail shoe':
                product_ids = ProductChoice.retail_shoe_product_ids_new
            elif product == 'after party friday':
                product_ids = ['2146481686', '2146532909', '2146507303', '2146481687']
            elif product:
                product_ids = [product]
            else:
                product_ids = ProductChoice.retail_bowling_ids_new_short

            data, num = DataDAO.get_centers(pagination=pagination,
                                            page_size=page_size,
                                            offset=offset,
                                            filters=filters,
                                            sort=sort,
                                            order=order,
                                            last_price=True,
                                            last_price_product_ids=product_ids,
                                            last_price_from_change=True,
                                            lastPriceSplit=True,
                                            columns=['center_name', 'region', 'district', 'brand', 'time_zone',
                                                     'center_type'],
                                            as_of_date=as_of_date
                                            )

            # data = data.where((pd.notnull(data)), "")
            data.columns = map(str.capitalize, data.columns)

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
            # elif type == 'excel':
            #     writer = pd.ExcelWriter('export.xlsx')
            #     response = data.to_excel(writer)
            #     writer.save()
            #     response = HttpResponse(response, content_type='application/vnd.ms-excel')
            #     response['Content-Disposition'] = 'attachment; filename=export.xlsx'
            else:
                response = json.dumps([], ensure_ascii=False)
                response = HttpResponse(response, content_type='application/json')
                response['Content-Disposition'] = 'attachment; filename=export.json'

            return response


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

            last_price_from_change = True

            # Non task date init
            # start = UDatetime.datetime_str_init(start)
            # start_report = start
            #
            # if not end:
            #     end = max(UDatetime.now_local() + datetime.timedelta(days=13),
            #               start + datetime.timedelta(days=13))
            #     end_report = None
            # else:
            #     end = UDatetime.datetime_str_init(end)
            #     end_report = end
            #
            # start = start.date()
            # end = end.date()

            start = UDatetime.datetime_str_init(start).date()
            if not end:
                end = None
            else:
                end = UDatetime.datetime_str_init(end).date()

            if product == 'retail bowling':
                np_price_symbol = request.GET.get('np-price-symbol')
                np_price = request.GET.get('np-price')
                np_price_unit = request.GET.get('np-price-unit')
                np_price_base = request.GET.get('np-price-base')
                primewk_price_symbol = request.GET.get('primewk-price-symbol')
                primewk_price = request.GET.get('primewk-price')
                primewk_price_unit = request.GET.get('primewk-price-unit')
                primewk_price_base = request.GET.get('primewk-price-base')
                primewkd_price_symbol = request.GET.get('primewkd-price-symbol')
                primewkd_price = request.GET.get('primewkd-price')
                primewkd_price_unit = request.GET.get('primewkd-price-unit')
                primewkd_price_base = request.GET.get('primewkd-price-base')
                premium_price_symbol = request.GET.get('premium-price-symbol')
                premium_price = request.GET.get('premium-price')
                premium_price_unit = request.GET.get('premium-price-unit')
                premium_price_base = request.GET.get('premium-price-base')

                price = [
                    {'product_id': '108',
                     'price_symbol': np_price_symbol,
                     'price_delta': UString.str2float(np_price),
                     'price_unit': np_price_unit,
                     'product_id_base': np_price_base},
                    {'product_id': '110',
                     'price_symbol': primewk_price_symbol,
                     'price_delta': UString.str2float(primewk_price),
                     'price_unit': primewk_price_unit,
                     'product_id_base': primewk_price_base},
                    {'product_id': '111',
                     'price_symbol': primewkd_price_symbol,
                     'price_delta': UString.str2float(primewkd_price),
                     'price_unit': primewkd_price_unit,
                     'product_id_base': primewkd_price_base},
                    {'product_id': '113',
                     'price_symbol': premium_price_symbol,
                     'price_delta': UString.str2float(premium_price),
                     'price_unit': premium_price_unit,
                     'product_id_base': premium_price_base},
                ]

                # Tracking
                tracking_type = TrackingType.objects.get(type='bulk retail bowling price change')
                content_type = ContentType.objects.get_for_model(RetailBowlingPrice)
            elif product == 'retail shoe':
                wk_price_symbol = request.GET.get('wk-price-symbol')
                wk_price = request.GET.get('wk-price')
                wk_price_unit = request.GET.get('wk-price-unit')
                wk_price_base = request.GET.get('wk-price-base')
                wknd_price_symbol = request.GET.get('wknd-price-symbol')
                wknd_price = request.GET.get('wknd-price')
                wknd_price_unit = request.GET.get('wknd-price-unit')
                wknd_price_base = request.GET.get('wknd-price-base')

                price = [
                    {'product_id': '114',
                     'price_symbol': wk_price_symbol,
                     'price_delta': UString.str2float(wk_price),
                     'price_unit': wk_price_unit,
                     'product_id_base': wk_price_base},
                    {'product_id': '115',
                     'price_symbol': wknd_price_symbol,
                     'price_delta': UString.str2float(wknd_price),
                     'price_unit': wknd_price_unit,
                     'product_id_base': wknd_price_base},
                ]

                # Tracking
                tracking_type = TrackingType.objects.get(type='bulk retail shoes price change')
                content_type = ContentType.objects.get_for_model(RetailShoePrice)
            elif product == 'after party friday':
                friday8PM_price_symbol = request.GET.get('8pm-price-symbol')
                friday8PM_price = request.GET.get('8pm-price')
                friday8PM_price_unit = request.GET.get('8pm-price-unit')
                friday8PM_price_base = request.GET.get('8pm-price-base')
                friday9PM_price_symbol = request.GET.get('9pm-price-symbol')
                friday9PM_price = request.GET.get('9pm-price')
                friday9PM_price_unit = request.GET.get('9pm-price-unit')
                friday9PM_price_base = request.GET.get('9pm-price-base')
                friday10PM_price_symbol = request.GET.get('10pm-price-symbol')
                friday10PM_price = request.GET.get('10pm-price')
                friday10PM_price_unit = request.GET.get('10pm-price-unit')
                friday10PM_price_base = request.GET.get('10pm-price-base')
                friday11PM_price_symbol = request.GET.get('11pm-price-symbol')
                friday11PM_price = request.GET.get('11pm-price')
                friday11PM_price_unit = request.GET.get('11pm-price-unit')
                friday11PM_price_base = request.GET.get('11pm-price-base')

                price = [
                    {'product_id': '2146481686',
                     'price_symbol': friday8PM_price_symbol,
                     'price_delta': UString.str2float(friday8PM_price),
                     'price_unit': friday8PM_price_unit,
                     'product_id_base': friday8PM_price_base},
                    {'product_id': '2146532909',
                     'price_symbol': friday9PM_price_symbol,
                     'price_delta': UString.str2float(friday9PM_price),
                     'price_unit': friday9PM_price_unit,
                     'product_id_base': friday9PM_price_base},
                    {'product_id': '2146507303',
                     'price_symbol': friday10PM_price_symbol,
                     'price_delta': UString.str2float(friday10PM_price),
                     'price_unit': friday10PM_price_unit,
                     'product_id_base': friday10PM_price_base},
                    {'product_id': '2146481687',
                     'price_symbol': friday11PM_price_symbol,
                     'price_delta': UString.str2float(friday11PM_price),
                     'price_unit': friday11PM_price_unit,
                     'product_id_base': friday11PM_price_base},
                ]

                # Tracking
                tracking_type = TrackingType.objects.get(type='bulk retail promos price change')
                content_type = ContentType.objects.get_for_model(ProductPrice)
            else:
                price_symbol = request.GET.get('price-symbol')
                price = request.GET.get('price')
                price_unit = request.GET.get('price-unit')

                price = [
                    {'product_id': product,
                     'price_symbol': price_symbol,
                     'price_delta': UString.str2float(price),
                     'price_unit': price_unit,
                     'product_id_base': product}
                ]

                # Tracking
                tracking_type = TrackingType.objects.get(type='bulk retail promos price change')
                content_type = ContentType.objects.get_for_model(ProductPrice)

            if not last_price_from_change:
                if not DOW:
                    DOW = [dow[0] for dow in DOW_choice]

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

            #
            msg = ''
            if price:
                if last_price_from_change:
                    bulk_price_change_task_from_price_change.delay(start, end, product, DOW, price, centers, request.user.username,
                                                 tracking_id=tracking_id.tracking_id)
                    # DataReviseDAO.pricing_new4(start, end, product, DOW, price, centers, request.user,
                    #                            tracking_id=tracking_id)
                else: #currently not being used
                    bulk_price_change_task.delay(start, end, product, DOW, price, centers, request.user.username,
                                                 tracking_id=tracking_id.tracking_id)
                    # DataReviseDAO.pricing_new3(start, end, product, DOW, price, centers, request.user,
                    #                            start_report, end_report, tracking_id=tracking_id)

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


