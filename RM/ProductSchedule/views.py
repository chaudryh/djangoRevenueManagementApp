import os
import numpy as np
import pandas as pd
import re
from datetime import datetime as dt
import pytz
import time

from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
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
    template_name = 'ProductSchedule/ProductScheduleIndex.html'
    return render(request, template_name)


class Panel1:
    class Form1:

        # result_path = os.path.join(BASE_DIR, 'media/RM/Centers/centers.xlsx')

        @classmethod
        def submit(cls, request, *args, **kwargs):

            columns = \
                [
                    {
                        'field': 'product_name', 'title': 'Product Name', 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center'
                    },
                    {
                        'field': 'freq', 'title': 'Freq', 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center'
                    },
                    {
                        'field': 'start', 'title': 'Start', 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center'
                    },
                    {
                        'field': 'end', 'title': 'End', 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center'
                    },
                    {
                        'field': 'DOW', 'title': 'DOW', 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center'
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

            data, num = DataDAO.get_productschedule(
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
            # Tracking
            current_user = request.user
            field = request.GET.get('field')
            new_value = request.GET.get(field)
            old_value = request.GET.get('old_value')

            center_id = request.GET.get('center_id')
            opt = request.GET.get('opt')
            product_name = request.GET.get('product_name')

            center_obj = Centers.objects.get(center_id=center_id)
            center_type = center_obj.center_type

            product_id = None
            product = Product.objects.filter(readable_product_name__contains=product_name)
            if product.exists() and product.count() == 1:
                product_id = product[0].product_id

            if product_name == 'Retail Prime Bowling':
                if center_type == 'traditional':
                    product_id = 105
                elif center_type == 'experiential':
                    product_id = 102
            elif product_name == 'Retail Premium Bowling':
                if center_type == 'traditional':
                    product_id = 106
                elif center_type == 'experiential':
                    product_id = 103
            product_obj = Product.objects.get(product_id=product_id)

            # Tracking
            tracking_type = TrackingType.objects.get(type='product opt in/out change')
            content_type = ContentType.objects.get_for_model(ProductSchedule)
            input_params = {field: new_value, 'old_value': old_value, 'center_id': center_id,
                            'product_name': product_name}
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

            ProductSchedule.objects \
                .filter(Q(product_id__product_id__exact=product_id) &
                        Q(center_id__center_id=center_id)) \
                .update(**{
                            'opt': opt,
                            'action_user': current_user,
                            'tracking_id': tracking_id
                           }
                        )

            return JsonResponse({})

