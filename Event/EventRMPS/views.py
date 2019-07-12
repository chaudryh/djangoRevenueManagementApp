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
from DAO.EventDataDAO import EventDataDao

# Create your views here.
# from .utils.LoadConfigData import LoadConfigData

EST = pytz.timezone(TIME_ZONE)
# Back
SpecialProds = ['Lane', 'Unlimited Arcade']
# SpecialProds = []


@staff_member_required(login_url='/login/')
@csrf_protect
def index(request, *args, **kwargs):
    template_name = 'EventRMPS/EventRMPSIndex.html'
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

            if selectType == 'sale_region':
                centers = Centers.objects.filter(status='open') \
                    .exclude(Q(sale_region=None) | Q(sale_region__contains='test'))

                if search:
                    centers = centers.filter(sale_region__contains=search)

                values = centers.values_list('sale_region', flat=True).distinct()
                values = sorted(values)

                # Skip Test centers dropdown
                values = [value for value in values if value not in ['Test', 'Test1']]

                result += \
                    [
                        {
                            'id': value,
                            "text": value,
                        }
                        for value in values
                    ]
            elif selectType == 'territory':
                centers = Centers.objects.filter(status='open') \
                    .exclude(Q(territory=None) | Q(territory__contains='test'))

                if search:
                    centers = centers.filter(territory__contains=search)

                values = centers.values_list('territory', flat=True).distinct()
                values = sorted(values)

                result += \
                    [
                        {
                            'id': value,
                            "text": value,
                        }
                        for value in values
                    ]
            # elif selectType == 'center_name':
            #     centers = Centers.objects.filter(status='open')
            #
            #     if search:
            #         centers = centers.filter(center_name__contains=search)
            #
            #     centers = centers \
            #         .order_by('center_id') \
            #         .extra(select={'center_id': 'CAST(center_id AS INTEGER)'})
            #
            #     center_records = pd.DataFrame.from_records(centers.values('center_id',
            #                                                               'center_name',
            #                                                               ))
            #     result += \
            #         [
            #             {
            #                 'id': row['center_id'],
            #                 "text": row['center_name'],
            #             }
            #             for index, row in center_records.iterrows()
            #         ]
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
            columns = request.GET.getlist('columns')

            # Find if all in the selections
            if columns and 'all' in columns:
                columns = []

            # Remove empty string
            columns = [column for column in columns if column]

            if columns:
                columnObjs = RMPS.objects \
                    .filter(reduce(operator.or_, (Q(attribute__startswith=column + '---')
                                                  for column in columns if column)))
            else:
                columnObjs = RMPS.objects.all()

            columnObjs = columnObjs.values('attribute', 'order').distinct().order_by('order')
            columnRecords = pd.DataFrame.from_records(columnObjs)
            columnRecords['attr1'], columnRecords['attr2'] = columnRecords['attribute'].str.split('---').str

            attr1, attr2 = columnRecords[['attr1', 'order', 'attribute']], columnRecords[['attr2', 'order', 'attribute']]

            attr1Agg = attr1.groupby('attr1').agg({'attr1': 'count', 'order': 'first', 'attribute': 'first'})
            attr1Agg.rename({'attr1': 'attr1_count'}, axis=1, inplace=True)
            attr1Agg.reset_index(inplace=True)
            attr1Agg.sort_values('order', inplace=True)

            columns0 = \
            [
                {
                    'field': 'center_id', 'title': 'Center Id',
                    'sortable': False,
                    'editable': False,
                    'align': 'center', 'vlign': 'center', 'rowspan': 2,
                    # 'filter': {'type': 'input'}
                },
                {
                    'field': 'center_name', 'title': 'Center Name',
                    'sortable': False,
                    'editable': False,
                    'align': 'center', 'vlign': 'center', 'rowspan': 2,
                    # 'filter': {'type': 'input'}
                },
                {
                    'field': 'sale_region', 'title': 'Sale Region',
                    'sortable': False,
                    'editable': False,
                    'align': 'center', 'vlign': 'center', 'rowspan': 2,
                    # 'filter': {'type': 'input'}
                },
                {
                    'field': 'territory', 'title': 'Territory',
                    'sortable': False,
                    'editable': False,
                    'align': 'center', 'vlign': 'center', 'rowspan': 2,
                    # 'filter': {'type': 'input'}
                },
                {
                    'field': 'arcade_type', 'title': 'Arcade Type',
                    'sortable': False,
                    'editable': False,
                    'align': 'center', 'vlign': 'center', 'rowspan': 2,
                    # 'filter': {'type': 'input'}
                },
            ]

            columns1 = []
            for index, row in attr1Agg.iterrows():
                # if row['attr1_count'] == 1:
                #     columns1 += \
                #         [
                #             {
                #                 'field': row['attribute'],
                #                 'title': row['attr1'].strip(),
                #                 # 'editable': True,
                #                 'align': 'center',
                #                 'vlign': 'center',
                #                 'rowspan': 2,
                #                 # 'filter': {'type': 'input'},
                #                 'editable': True,
                #                 'min-width': 400,
                #             }
                #         ]
                # else:
                    columns1 += \
                        [
                            {
                                'field': row['attribute'],
                                'title': row['attr1'].strip(),
                                'align': 'center',
                                'vlign': 'center',
                                'colspan': row['attr1_count'],
                                'min-width': 100,
                            }
                        ]

            columns2 = []
            for index, row in attr2.iterrows():
                if row['attr2']:
                    columns2 += \
                        [
                            {
                                'field': row['attribute'],
                                'title': row['attr2'].strip(),
                                'align': 'center',
                                'vlign': 'center',
                                'editable': True,
                                'min-width': 400,
                                # 'filter': {'type': 'input'}
                            }
                        ]

            columns = [columns0 + columns1, columns2]

            return JsonResponse({'status': 1, 'msg': '', 'columns': columns})

        @staticmethod
        def create(request, *args, **kwargs):
            page_size = int(request.GET.get('limit'))
            offset = int(request.GET.get('offset'))
            filters = request.GET.get('filter')
            sort = request.GET.get('sort')
            order = request.GET.get('order')

            # Get all selection values
            sale_region = request.GET.getlist('sale_region[]')
            territory = request.GET.getlist('territory[]')
            center_id = request.GET.getlist('center_id[]')
            center_name = request.GET.getlist('center_name[]')
            columns = request.GET.getlist('columns[]')

            # Find if all in the selections
            if sale_region and 'all' in sale_region:
                sale_region = []
            if territory and 'all' in territory:
                territory = []
            if center_id and 'all' in center_id:
                center_id = []
            if center_name and 'all' in center_name:
                center_name = []
            if columns and 'all' in columns:
                columns = []

            # Remove empty string
            sale_region = [item for item in sale_region if item]
            territory = [item for item in territory if item]
            center_id = [item for item in center_id if item]
            center_name = [item for item in center_name if item]
            columns = [item for item in columns if item]

            data, num = EventDataDao.get_event_RMPS(sale_region, territory, center_id, center_name, columns,
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
        @permission_required('Models.change_eventtier', raise_exception=False)
        def edit(request, *args, **kwargs):
            current_user = request.user

            field = request.GET.get('field')
            new_value = request.GET.get(field)
            old_value = request.GET.get('old_value')
            center_id = request.GET.get('center_id')

            center_obj = Centers.objects.get(center_id=center_id)

            # Check if dollar unit
            rmps = RMPS.objects.filter(attribute=field)[0]
            unit = rmps.unit
            order = rmps.order

            # Tracking
            tracking_type = TrackingType.objects.get(type='event change')
            content_type = ContentType.objects.get_for_model(RMPS)
            input_params = {'center_id': center_id, 'field': field, 'new_value': new_value, 'old_value': old_value}
            tracking_id = Tracking.objects.create(
                username=current_user,
                tracking_type=tracking_type,
                content_type=content_type,
                input_params=input_params
            )
            #

            # clean price value
            old_value = old_value.replace('$', '')
            new_value = new_value.replace('$', '')

            if old_value in [None, '', '-']:
                old_value = None
            if new_value in [None, '', '-']:
                new_value = None
            # validate price is a number and positive
            if unit == 'dollar' and new_value and not new_value.replace('.', '').isdigit():
                try:
                    new_value = float(new_value)
                    if new_value < 0:
                        return JsonResponse({'status': 0, 'msg': 'Please input a positive number'})
                except Exception as e:
                    return JsonResponse({'status': 0, 'msg': 'Please input a valid number'})

            # Tracking Change Report
            if unit == 'dollar':
                EventChangeReport.objects.create(
                    tracking_id=tracking_id,
                    username=current_user,
                    center_id=center_obj,
                    product_RMPS=field,
                    price_old=old_value,
                    price_new=new_value,
                )
            #

            #
            RMPS.objects \
                .update_or_create(
                    center_id=center_obj,
                    attribute=field,
                    defaults={
                        'value': new_value,
                        'action_user': current_user,
                        'unit': unit,
                        'order': order,
                        'tracking_id': tracking_id,
                    }
                )

            return JsonResponse({'status': 1, 'msg': ''})
