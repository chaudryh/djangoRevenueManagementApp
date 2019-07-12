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

from DAO.DataDAO import *

from utils.UTable import UTable

# Create your views here.
# from .utils.LoadConfigData import LoadConfigData

EST = pytz.timezone(TIME_ZONE)
DEFAULT_RANGE = datetime.timedelta(days=6)


@staff_member_required(login_url='/login/')
@csrf_protect
def index(request, *args, **kwargs):
    template_name = 'PricingTable/PricingTableIndex.html'
    return render(request, template_name)


class Panel1:
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
            product_list = request.GET.getlist('product[]')

            start = UDatetime.datetime_str_init(start).date()
            end = UDatetime.datetime_str_init(end, start, default_delta=DEFAULT_RANGE)
            if type(end) == datetime.datetime:
                end = end.date()

            # init product_list
            product_list_new = []
            for product_ids in product_list:
                product_list_new += product_ids.split(',')

            data, num = DataDAO.get_price_table(start, end, product_list_new,
                                                pagination=True,
                                                page_size=page_size,
                                                offset=offset,
                                                filters=filters,
                                                sort=sort,
                                                order=order
                                                )
            data = data.where((pd.notnull(data)), "-")

            if not data.empty:
                data_response = data.to_dict(orient='records')
                # data_response = [
                #     {'product':'bowling', 'center_id': '102', 'center_name': 'AMF Williamsburg Lanes', '20180302-nonprime':1},
                #     {'product': 'shoe', 'center_id': '102', 'center_name': 'AMF Williamsburg Lanes', '20180302-nonprime': 1},
                #     {'product': 'food', 'center_id': '102', 'center_name': 'AMF Williamsburg Lanes', '20180302-nonprime': 1},
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
            # print(response)
            return JsonResponse(response, safe=False)

        @staticmethod
        def export(request, *args, **kwargs):
            page_size = int(request.GET.get('limit'))
            offset = int(request.GET.get('offset'))
            filters = request.GET.get('filter')
            sort = request.GET.get('sort')
            order = request.GET.get('order')
            start = request.GET.get('start')
            end = request.GET.get('end')
            file_type = request.GET.get('type')
            product_list = request.GET.getlist('product[]')

            start = UDatetime.datetime_str_init(start).date()
            end = UDatetime.datetime_str_init(end, start, default_delta=DEFAULT_RANGE)
            if type(end) == datetime.datetime:
                end = end.date()

            # init product_list
            product_list_new = []
            for product_ids in product_list:
                product_list_new += product_ids.split(',')

            data, num = DataDAO.get_price_table(start, end, product_list_new,
                                                pagination=True,
                                                page_size=page_size,
                                                offset=offset,
                                                filters=filters,
                                                sort=sort,
                                                order=order
                                                )
            data = data.where((pd.notnull(data)), "")
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

        @staticmethod
        @permission_required('Pricing.change_retailbowlingprice', raise_exception=True)
        def edit_old(request, *args, **kwargs):

            current_user = request.user
            field = request.GET.get('field')
            new_value = request.GET.get(field)
            old_value = request.GET.get('old_value')
            center_id = request.GET.get('center_id')
            date = request.GET.get('field')
            product = request.GET.get('product')
            product_id = request.GET.get('product_id')

            center_obj = Centers.objects.get(center_id=center_id)
            center_type = center_obj.center_type

            date = dt.strptime(date, '%Y-%m-%d')
            DOW = DOW_choice[date.weekday()][0]
            date = date.date()

            if old_value == '-':
                old_value = None
            if old_value:
                old_value = old_value.replace('$', '')
                old_value = round(float(old_value), 2)

            if new_value in ['', '-']:
                new_value = None
            if new_value:
                new_value = new_value.replace('$', '')
                new_value = round(float(new_value), 2)

            products_obj = Product.objects.filter(product_id=product_id)
            product_obj = None
            model = None
            if products_obj.exists():
                if products_obj.count() == 1:
                    product_obj = products_obj[0]
                elif products_obj.count() > 1:
                    products_obj = products_obj.filter(product_name__contains=center_type)
                    if products_obj.count() == 1:
                        product_obj = products_obj[0]

            if product_obj:
                if product_obj.report_type == 'Retail Bowling':
                    model = RetailBowlingPrice
                elif product_obj.report_type == 'Retail Shoe':
                    model = RetailShoePrice
                else:
                    model = ProductPrice

            # if product in ['NP Bowl', 'P Bowl', 'Prem Bowl']:
            #     model = RetailBowlingPrice
            #     if center_type == 'experiential' and product == 'NP Bowl':
            #         product_name = 'retail experiential non-prime bowling'
            #     if center_type == 'experiential' and product == 'P Bowl':
            #         product_name = 'retail experiential prime bowling'
            #     if center_type == 'experiential' and product == 'Prem Bowl':
            #         product_name = 'retail experiential premium bowling'
            #     if center_type == 'traditional' and product == 'NP Bowl':
            #         product_name = 'retail traditional non-prime bowling'
            #     if center_type == 'traditional' and product == 'P Bowl':
            #         product_name = 'retail traditional prime bowling'
            #     if center_type == 'traditional' and product == 'Prem Bowl':
            #         product_name = 'retail traditional premium bowling'
            # elif product in ['Shoe']:
            #     model = RetailShoePrice
            #     product_name = 'retail shoe'
            # else:
            #     model = ProductPrice
            #     if product == 'SunFun Bowl':
            #         product_name = 'Sunday Funday Bowling'
            #     if product == 'SunFun Shoe':
            #         product_name = 'Sunday Funday Shoes'
            #     if product == 'Mon Mayh':
            #         product_name = 'Monday Mayhem AYCB'
            #     if product == '222 Tue':
            #         product_name = '222 Tuesday Game'
            #     if product == 'Colg Nt Wed':
            #         product_name = 'College night Wed'
            #     if product == 'Colg Nt Thu':
            #         product_name = 'College night Thu'

            # Tracking
            tracking_type = TrackingType.objects.get(type='retail price table price change')
            content_type = ContentType.objects.get_for_model(model)
            input_params = {'price': new_value, 'old_value': old_value, 'date': field, 'center_id': center_id,
                            'product_id': product_obj.product_id, 'product_name': product_obj.product_name}
            tracking_id = Tracking.objects.create(
                username=current_user,
                tracking_type=tracking_type,
                content_type=content_type,
                input_params=input_params
            )
            # Tracking Change Report
            BSChangeReport.objects.create(
                tracking_id=tracking_id,
                username=current_user,
                center_id=center_obj,
                product_id=product_obj,
                effective_start=date,
                effective_end=date,
                price_old=old_value,
                price_new=new_value,
                is_bulk_change=False
            )
            #

            if product_obj:
                if new_value:
                    model.objects \
                        .update_or_create(
                            center_id=center_obj,
                            date=date,
                            DOW=DOW,
                            product_id=product_obj,
                            defaults={
                                'product_name': product_obj.product_name,
                                'price': new_value,
                                'action_user': current_user,
                                'tracking_id': tracking_id
                            }
                        )
                elif not new_value:
                    model.objects \
                        .filter(
                            center_id=center_id,
                            date=date,
                            DOW=DOW,
                            product_name=product_obj.product_name,
                        ) \
                        .delete()

            return JsonResponse({})

        @staticmethod
        @permission_required('Pricing.change_retailbowlingprice', raise_exception=True)
        def edit(request, *args, **kwargs):

            current_user = request.user
            field = request.GET.get('field')
            new_value = request.GET.get(field)
            old_value = request.GET.get('old_value')
            center_id = request.GET.get('center_id')
            date = request.GET.get('field')
            product = request.GET.get('product')
            product_id = request.GET.get('product_id')

            center_obj = Centers.objects.get(center_id=center_id)
            center_type = center_obj.center_type

            date = dt.strptime(date, '%Y-%m-%d')
            DOW = DOW_choice[date.weekday()][0]
            date = date.date()

            if old_value == '-':
                old_value = None
            if old_value:
                old_value = old_value.replace('$', '')
                old_value = round(float(old_value), 2)

            if new_value in ['', '-']:
                new_value = None
            if new_value:
                new_value = new_value.replace('$', '')
                new_value = round(float(new_value), 2)

            product_obj = Product.objects.get(product_id=product_id)

            # Tracking
            tracking_type = TrackingType.objects.get(type='retail price table price change')
            content_type = ContentType.objects.get_for_model(ProductPrice)
            input_params = {'price': new_value, 'old_value': old_value, 'date': field, 'center_id': center_id,
                            'product_id': product_obj.product_id, 'product_name': product_obj.product_name}
            tracking_id = Tracking.objects.create(
                username=current_user,
                tracking_type=tracking_type,
                content_type=content_type,
                input_params=input_params
            )
            # Tracking Change Report
            BSChangeReport.objects.create(
                tracking_id=tracking_id,
                username=current_user,
                center_id=center_obj,
                product_id=product_obj,
                effective_start=date,
                effective_end=date,
                price_old=old_value,
                price_new=new_value,
                is_bulk_change=False,
                action_time=UDatetime.now_local()
            )
            #

            if product_obj:
                if new_value:
                    ProductPriceChange.objects \
                        .update_or_create(
                        center_id=center_obj,
                        start=date,
                        end=date,
                        # DOW=DOW,
                        product_id=product_obj,
                        action_time=UDatetime.now_local(),
                        defaults={
                            'price': round(new_value, 2),
                            'perpetual': False,
                            'product_name': product_obj.product_name,
                            'action_user': current_user,
                            'tracking_id': tracking_id
                        }
                    )
                elif not new_value:
                    ProductPriceChange.objects \
                        .update_or_create(
                        center_id=center_obj,
                        start=date,
                        end=date,
                        # DOW=DOW,
                        product_id=product_obj,
                        action_time=UDatetime.now_local(),
                        defaults={
                            'price': None,
                            'perpetual': False,
                            'product_name': product_obj.product_name,
                            'action_user': current_user,
                            'tracking_id': tracking_id
                        }
                    )

            return JsonResponse({})


class Panel2:
    class Form1:
        @classmethod
        def submit(cls, request, *args, **kwargs):
            start = request.GET.get('start')
            end = request.GET.get('end')

            start = UDatetime.datetime_str_init(start)
            end = UDatetime.datetime_str_init(end, start, default_delta=DEFAULT_RANGE)

            date_range = UDatetime.date_range(start, end)

            # make up columns
            columns_list = \
            [
                {'field': 'center_id', 'title': 'Id'},
                {'field': 'center_name', 'title': 'Name'},
                {'field': 'district', 'title': 'District'},
                {'field': 'region', 'title': 'Region'},
                {'field': 'brand', 'title': 'Brand'},
                {'field': 'bowling_tier', 'title': 'Bowling Tier'},
                {'field': 'food_tier', 'title': 'Food Tier'},
                {'field': 'food_menu', 'title': 'Food Menu'},
            ]
            columns = \
                [
                    {
                        'field': column_list['field'], 'title': column_list['title'], 'sortable': False, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    }
                    for column_list in columns_list
                ]
            columns += \
                [
                    {
                        'field': 'product_name', 'title': 'Product', 'sortable': False, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'width': 100
                    },
                    {
                        'field': 'opt', 'title': 'Opt', 'sortable': False, 'editable': False,
                        'align': 'center', 'vlign': 'center'
                    },
                    {
                        'field': 'product_id', 'title': 'Product Id', 'sortable': False, 'editable': False,
                        'visible': False, 'align': 'center', 'vlign': 'center'
                    }
                ]

            columns += \
            [
                {
                    'field': str(date.date()),
                    'title': '{dow}<br/>{date}'.format(dow=DOW_choice[date.weekday()][0].capitalize(), date=str(date.strftime('%m/%d/%y'))),
                    'editable': True,
                    'align': 'center',
                    'vlign': 'center',
                }
                for date in date_range
            ]

            return JsonResponse({'status': 1, 'msg': '', 'columns': columns})

        @classmethod
        def submit_old(cls, request, *args, **kwargs):
            start = request.GET.get('start')
            end = request.GET.get('end')

            start = UDatetime.datetime_str_init(start)
            end = UDatetime.datetime_str_init(end, default_delta=DEFAULT_RANGE)

            # make up columns
            columns_main = UTable.create_columns(
                [
                    {'field': 'center_id', 'title': 'Id'},
                    {'field': 'center_name', 'title': 'Name'},
                    {'field': 'district', 'title': 'District'},
                    {'field': 'region', 'title': 'Region'},
                    {'field': 'brand', 'title': 'Brand'},
                    {'field': 'bowling_tier', 'title': 'Tier'},
                    {'field': 'product', 'title': 'Product'},
                    {'field': 'food_menu', 'title': 'Food Menu'},
                ]
            )
            columns_date_level1 = UTable.create_columns_by_date_range(start, end, level=1)
            columns_date_level2 = UTable.create_columns_by_date_range(start, end, level=2)
            columns = [
                columns_main + columns_date_level1,
                columns_date_level2
            ]

            return JsonResponse({'status': 1, 'msg': '', 'columns': columns})
