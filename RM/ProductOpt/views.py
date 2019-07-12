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

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
from django.views.decorators.csrf import csrf_protect, csrf_exempt

from bowlero_backend.settings import TIME_ZONE, BASE_DIR
from .models.models import *

from DAO.DataDAO import *

from Celery.tasks import *

from utils.UTable import UTable

# Create your views here.
# from .utils.LoadConfigData import LoadConfigData

EST = pytz.timezone(TIME_ZONE)


@staff_member_required(login_url='/login/')
@csrf_protect
def index(request, *args, **kwargs):
    template_name = 'ProductOpt/ProductOptIndex.html'
    return render(request, template_name)


class Panel1:
    class Form1:

        # result_path = os.path.join(BASE_DIR, 'media/RM/Centers/centers.xlsx')

        @classmethod
        def submit(cls, request, *args, **kwargs):

            columns = Panel2.Table1.get_columns(request, *args, **kwargs)

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
        def get_products():
            #removing certain products by product ID bc they always opt in
            remove_product_list = ['101', '102', '103', '104', '105', '106', '108', '109', '111', '112', '2011']
            product_obj = Product.objects \
                .filter(
                    report_type__in=[
                        'Retail Bowling',
                        'Retail Promos',
                    ],
                    status='active',
                    order__isnull=False
                ) \
                .exclude(
                    product_id__in=remove_product_list
                )
            #Use pandas to extract the values of certain columns and then reorder them
            product_records = pd.DataFrame.from_records(product_obj.values('product_id',
                                                                           'product_num',
                                                                           'short_product_name',
                                                                           'order',
                                                                           ))

            # change sunday funday
            product_records.loc[product_records['product_id'] == '2010', 'short_product_name'] = 'SunFun'
            product_records.sort_values(['order'], inplace=True)

            return product_records

        @classmethod
        def get_columns(cls, request, *args, **kwargs):

            product_records = cls.get_products()
            products_list = product_records.to_dict('records')

            columns = \
                [
                    {
                        'field': 'center_id', 'title': 'Center Id', 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'center_name', 'title': 'Center Name', 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                ]

            # columns += [
            #     {
            #         'field': '102,105', 'title': 'Weekday Retail Prime Bowling', 'sortable': False, 'editable': True,
            #         'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
            #     },
            #     {
            #         'field': '103,106', 'title': 'Weekend Retail Premium Bowling', 'sortable': False,
            #         'editable': True,
            #         'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
            #     }
            # ]

            columns += [
                {
                    'field': product['product_id'], 'title': product['short_product_name'],
                    'sortable': False, 'editable': True,
                    'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                }
                for product in products_list
            ]

            return columns

        @staticmethod
        def create(request, *args, **kwargs):
            page_size = int(request.GET.get('limit'))
            offset = int(request.GET.get('offset'))
            filters = request.GET.get('filter')
            sort = request.GET.get('sort')
            order = request.GET.get('order')
            date = request.GET.get('date')

            date = UDatetime.datetime_str_init(date).date()

            data, num = DataDAO.get_productopt(
                                                 date=date,
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
        #This version of the edit function is no longer being used
        def edit_old(request, *args, **kwargs):
            # Tracking
            current_user = request.user
            field = request.GET.get('field')
            new_value = request.GET.get(field)
            old_value = request.GET.get('old_value')

            center_id = request.GET.get('center_id')
            opt = request.GET.get(field)
            product_ids = field
            center_obj = Centers.objects.get(center_id=center_id)
            center_type = center_obj.center_type

            product_ids = product_ids.split(',')

            if product_ids == ['102', '105']:
                if center_type == 'traditional':
                    product_ids = ['105']
                elif center_type == 'experiential':
                    product_ids = ['102']
            elif product_ids == ['103', '106']:
                if center_type == 'traditional':
                    product_ids = ['106']
                elif center_type == 'experiential':
                    product_ids = ['103']

            if product_ids == ['2010']:
                product_ids = ['2010', '2011']

            for product_id in product_ids:

                product_obj = Product.objects.get(product_id=product_id)

                # Tracking
                tracking_type = TrackingType.objects.get(type='product opt in/out change')
                content_type = ContentType.objects.get_for_model(ProductOpt)
                input_params = {field: new_value, 'old_value': old_value, 'center_id': center_id,
                                'product_id': product_id}
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
                    effective_start=None,
                    effective_end=None,
                    price_old=None,
                    price_new=None,
                    is_bulk_change=False,
                    opt=opt
                )
                #

                ProductOpt.objects \
                    .filter(Q(product_id__product_id=product_id) &
                            Q(center_id__center_id=center_id)) \
                    .update(**{
                                'opt': opt,
                                'action_user': current_user,
                                'tracking_id': tracking_id
                               }
                            )

            return JsonResponse({})

        @staticmethod
        @permission_required('Pricing.change_retailbowlingprice', raise_exception=False)
        def edit(request, *args, **kwargs):
            # Tracking
            current_user = request.user
            field = request.GET.get('field')
            new_value = request.GET.get(field)
            old_value = request.GET.get('old_value')
            #Check for validations here on the back end

            center_id = request.GET.get('center_id')
            opt = request.GET.get(field)
            product_ids = field
            center_obj = Centers.objects.get(center_id=center_id)
            center_type = center_obj.center_type
            date = request.GET.get('date')

            product_ids = product_ids.split(',')
            date = UDatetime.datetime_str_init(date).date()

            # opt validate
            opt = opt.lower().capitalize()
            if opt not in ['In', 'Out']:
                return JsonResponse({})

            if product_ids == ['102', '105']:
                if center_type == 'traditional':
                    product_ids = ['105']
                elif center_type == 'experiential':
                    product_ids = ['102']
            elif product_ids == ['103', '106']:
                if center_type == 'traditional':
                    product_ids = ['106']
                elif center_type == 'experiential':
                    product_ids = ['103']

            if product_ids == ['2010']:
                product_ids = ['2010', '2011']

            for product_id in product_ids:

                product_obj = Product.objects.get(product_id=product_id)

                # Tracking page edits for use in Audit report
                tracking_type = TrackingType.objects.get(type='product opt in/out change')
                content_type = ContentType.objects.get_for_model(ProductOpt)
                input_params = {field: new_value, 'old_value': old_value, 'center_id': center_id,
                                'product_id': product_id}
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
                    effective_end=None,
                    price_old=None,
                    price_new=None,
                    is_bulk_change=False,
                    opt=opt
                )
                #

                ProductOpt.objects \
                    .update_or_create(
                        product_id=product_obj,
                        center_id=center_obj,
                        start=date,
                        end=None,
                        defaults={
                            'opt': opt,
                            'action_user': current_user,
                            'tracking_id': tracking_id,
                            'action_time': UDatetime.now_local()
                        }
                    )

            # retail bowling opt in/out

            if product_ids[0] in ProductChoice.products_opt_oppo:

                if opt == 'In':
                    opt_oppo = 'Out'
                elif opt == 'Out':
                    opt_oppo = 'In'
                else:
                    return JsonResponse({})

                product_id = ProductChoice.products_opt_oppo_dict[product_ids[0]]

                product_obj = Product.objects.get(product_id=product_id)

                # Tracking
                tracking_type = TrackingType.objects.get(type='product opt in/out change')
                content_type = ContentType.objects.get_for_model(ProductOpt)
                input_params = {field: new_value, 'old_value': old_value, 'center_id': center_id,
                                'product_id': product_id}
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
                    effective_end=None,
                    price_old=None,
                    price_new=None,
                    is_bulk_change=False,
                    opt=opt_oppo
                )
                #

                ProductOpt.objects \
                    .update_or_create(
                        product_id=product_obj,
                        center_id=center_obj,
                        start=date,
                        end=None,
                        defaults={
                            'opt': opt_oppo,
                            'action_user': current_user,
                            'tracking_id': tracking_id,
                            'action_time': UDatetime.now_local()
                        }
                    )

            return JsonResponse({})

        @classmethod
        def export(cls, request, *args, **kwargs):
            page_size = int(request.GET.get('limit'))
            offset = int(request.GET.get('offset'))
            filters = request.GET.get('filter')
            sort = request.GET.get('sort')
            order = request.GET.get('order')
            date = request.GET.get('date')
            file_type = request.GET.get('type')

            date = UDatetime.datetime_str_init(date).date()

            data, num = DataDAO.get_productopt(
                                                 date=date,
                                                 pagination=True,
                                                 page_size=page_size,
                                                 offset=offset,
                                                 filters=filters,
                                                 sort=sort,
                                                 order=order,
                                               )

            # Replace columns
            product_records = cls.get_products()
            product_records['name'] = \
                product_records['short_product_name'] + ' {' + product_records['product_num'] + '}'
            product_map = dict(zip(product_records['product_id'], product_records['name']))
            columns = ['center_id', 'center_name'] + product_records['product_id'].tolist()
            data = data.reindex(columns=columns)
            data.rename(columns=product_map, inplace=True)
            data['center_id'] = data['center_id'].astype(int)

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

                response = HttpResponse(response.read(),
                                        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                                        )
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

            start = request.POST.get('start')
            end = request.POST.get('end')
            current_user = request.user

            try:
                file = request.FILES.getlist('FileUpload')[0]
            except Exception as e:
                return JsonResponse({'status': 0, 'msg': 'No attached file'})

            try:
                data = pd.read_excel(file)
                data = pd.melt(data,
                               id_vars=['center_id', 'center_name'],
                               var_name='product_num',
                               value_name='opt'
                               )
                data.dropna(subset=['opt'], inplace=True)
                data['product_num'] = data['product_num'].str.extract(r'{(\d*)}', expand=False)

                # data validation, skip non-validated value
                data['opt'] = data['opt'].str.lower()
                data['opt'] = data['opt'].str.capitalize()
                data = data[data['opt'].isin(['In', 'Out'])]

                bulk_product_opt.delay(data.to_dict(), current_user.username, start, end)

                msg = "RMS is updating your opt changes. Opt changes for all centers may take up to 15 mins. " \
                      "Subsequently the changes will be displayed in the 'Change Report'."
            except Exception as e:
                msg = "File is not able to be parsed and processed. Make sure your file format is correct."
                return JsonResponse({'status': 0, 'msg': msg})

            return JsonResponse({'status': 1, 'msg': msg})
