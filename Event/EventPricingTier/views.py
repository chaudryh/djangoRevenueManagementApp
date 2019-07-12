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
# Back
SpecialProds = ['Lane', 'Unlimited Arcade']
# SpecialProds = []

@staff_member_required(login_url='/login/')
@csrf_protect
def index(request, *args, **kwargs):
    template_name = 'EventPricingTier/EventPricingTierIndex.html'
    return render(request, template_name)


class Panel1:
    class Form1:

        # result_path = os.path.join(BASE_DIR, 'media/RM/Centers/centers.xlsx')

        @classmethod
        def submit(cls, request, *args, **kwargs):
            response = Panel2.Table1.get_columns(request=request)

            return response

        @classmethod
        def get_product(cls, request, *args, **kwargs):
            selectType = request.GET.get('selectType')
            group = request.GET.get('group')
            subGroup = request.GET.get('subGroup')
            tier = request.GET.get('tier')

            if selectType == 'group':
                tier_list = EventTier.objects.filter().values_list('group', flat=True).distinct()
                tier_list = sorted(tier_list)
            elif selectType == 'subGroup':
                if group in SpecialProds:
                    tier_list = ['NA']
                else:
                    tier_list = EventTier.objects.filter(group=group).values_list('subGroup', flat=True).distinct()
                    tier_list = sorted(tier_list)
            elif selectType == 'tier':
                if group in SpecialProds:
                    tier_list = EventTier.objects.filter(group=group)
                    tier_list = tier_list.values_list('tier', flat=True).distinct()
                else:
                    tier_list = EventTier.objects.filter(group=group, subGroup=subGroup)
                    tier_list = tier_list.values_list('tier', flat=True).distinct()
                    tier_list = ['All'] + list(tier_list)
            else:
                return JsonResponse({'status': 1, 'msg': '', 'results': []})

            result = \
                [
                    {
                        'id': item,
                        "text": item,
                    }
                    for item in tier_list
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

            group = request.GET.get('group')
            subGroup = request.GET.get('subGroup')
            tier = request.GET.get('tier')

            if group in SpecialProds:
                columns_product = EventTier.objects.filter(group=group)
            else:
                columns_product = EventTier.objects.filter(group=group, subGroup=subGroup)
                if tier and tier != 'All':
                    columns_product = columns_product.filter(tier=tier)

            columns_product = columns_product \
                .values_list('product', flat=True) \
                .distinct()

            if group in SpecialProds:
                columns = \
                    [
                        {
                            'field': 'subGroup', 'title': 'Duration', 'sortable': True, 'editable': False,
                            'align': 'center', 'vlign': 'center',
                            # 'filter': {'type': 'input'}
                        },
                    ]
            else:
                columns = \
                [
                    {
                        'field': 'tier', 'title': 'Tier', 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center',
                        # 'filter': {'type': 'input'}
                    },
                ]

            columns += \
                [
                    {
                        'field': column_product,
                        'title': column_product,
                        'editable': True,
                        'align': 'center',
                        'vlign': 'center',
                    }
                    for column_product in columns_product
                ]

            return JsonResponse({'status': 1, 'msg': '', 'columns': columns})

        @staticmethod
        def create(request, *args, **kwargs):
            page_size = int(request.GET.get('limit'))
            offset = int(request.GET.get('offset'))
            filters = request.GET.get('filter')
            sort = request.GET.get('sort')
            order = request.GET.get('order')

            group = request.GET.get('group')
            subGroup = request.GET.get('subGroup')
            tier = request.GET.get('tier')

            data, num = GetEvent.get_event_price_tier(group, subGroup, tier,
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
        @permission_required('Models.change_eventtier', raise_exception=True)
        def edit(request, *args, **kwargs):
            # Tracking
            current_user = request.user
            report_type = request.GET.get('product')
            order = request.GET.get('order')

            field = request.GET.get('field')
            new_value = request.GET.get(field)
            old_value = request.GET.get('old_value')
            product = field

            group = request.GET.get('group')
            subGroup = request.GET.get('subGroup')
            tier = request.GET.get('tier')
            subGroupSelect = request.GET.get('subGroupSelect')
            tierSelect = request.GET.get('tierSelect')

            old_value = old_value.replace('$', '')
            new_value = new_value.replace('$', '')

            if not new_value:
                new_value = None

            if group in SpecialProds:
                # Tracking
                tracking_type_name = 'retail bowling tier price change'
                tracking_type = TrackingType.objects.get(type=tracking_type_name)
                content_type = ContentType.objects.get_for_model(ProductPrice)
                input_params = {'price': new_value,
                                'old_value': old_value,
                                'group': group,
                                'subGroup': subGroup,
                                'product': product,
                                'tier': tierSelect,
                                'report type': report_type,
                                'order': order
                                }
                tracking_id = Tracking.objects.create(
                    username=current_user,
                    tracking_type=tracking_type,
                    content_type=content_type,
                    input_params=input_params
                )
                #
                EventTier.objects \
                    .update_or_create(
                        tier=tierSelect,
                        group=group,
                        subGroup=subGroup,
                        product=product,
                        defaults={
                            'price': new_value,
                            'action_user': current_user,
                            'tracking_id': tracking_id
                        }
                )
            else:
                # Tracking
                tracking_type_name = 'retail bowling tier price change'
                tracking_type = TrackingType.objects.get(type=tracking_type_name)
                content_type = ContentType.objects.get_for_model(ProductPrice)
                input_params = {'price': new_value,
                                'old_value': old_value,
                                'group': group,
                                'subGroup': subGroupSelect,
                                'product': product,
                                'tier': tier,
                                'report type': report_type,
                                'order': order
                                }
                tracking_id = Tracking.objects.create(
                    username=current_user,
                    tracking_type=tracking_type,
                    content_type=content_type,
                    input_params=input_params
                )
                #
                EventTier.objects \
                    .update_or_create(
                        tier=tier,
                        group=group,
                        subGroup=subGroupSelect,
                        product=product,
                        defaults={
                            # 'price': new_value,
                            # Back
                            'price': new_value if new_value else None,
                            'action_user': current_user,
                            'tracking_id': tracking_id
                        }
                    )

            return JsonResponse({})
