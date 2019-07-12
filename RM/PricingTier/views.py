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
    template_name = 'PricingTier/PricingTierIndex.html'
    return render(request, template_name)


class Panel1:
    class Form1:

        # result_path = os.path.join(BASE_DIR, 'media/RM/Centers/centers.xlsx')

        @classmethod
        def submit(cls, request, *args, **kwargs):
            center_type = request.GET.get('center_type')
            product = request.GET.get('product')

            if not center_type:
                center_type = 'experiential'
            if not product:
                product = 'bowling'

            product_ids = []
            if center_type == 'traditional' and product == 'bowling':
                product_ids = ProductChoice.retail_bowling_traditional_center
            elif center_type == 'experiential' and product == 'bowling':
                product_ids = ProductChoice.retail_bowling_experiential_center
            elif product == 'shoes':
                product_ids = ProductChoice.retail_shoe_product_ids

            pricing_tier = PricingTierTable.objects \
                .filter(product_id__in=product_ids,
                        center_type=center_type)\
                .values_list('tier', flat=True)\
                .distinct()

            tiers = pricing_tier

            columns_first_level = \
                [
                    {
                        'field': 'DOW', 'title': 'DOW', 'sortable': True, 'editable': False, 'rowspan': 2,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'time', 'title': 'Time', 'sortable': True, 'editable': True, 'rowspan': 2,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'period_label', 'title': 'Period', 'sortable': True, 'editable': False, 'rowspan': 2,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                ]

            columns_first_level += [
                {
                    'field': 'tier',
                    'title': 'Tier',
                    'colspan': len(tiers),
                    'align': 'center',
                }
            ]

            columns_second_level = \
            [
                {
                    'field': tier,
                    'title': tier,
                    'editable': True,
                    'align': 'center',
                    'vlign': 'center',
                }
                for tier in tiers
            ]

            columns = [columns_first_level, columns_second_level]

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
            center_type = request.GET.get('center_type')
            product = request.GET.get('product')

            if not center_type:
                center_type = 'experiential'
            if not product:
                product = 'bowling'

            data, num = DataDAO.get_price_tier(center_type, product,
                                               pagination=True,
                                               page_size=page_size,
                                               offset=offset,
                                               filters=filters,
                                               sort=sort,
                                               order=order
                                               )

            if not data.empty:
                data['DOW'] = data['DOW'].apply(lambda x: x.capitalize())
                data['period_label'] = data['period_label'].apply(lambda x: x.capitalize())
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
        @permission_required('Pricing.change_pricingtiertable', raise_exception=True)
        def edit(request, *args, **kwargs):
            # Tracking
            current_user = request.user

            center_type = request.GET.get('center_type')
            product = request.GET.get('product')
            DOW = request.GET.get('DOW')
            period_label = request.GET.get('period_label')
            tier_time = request.GET.get('time')
            order = request.GET.get('order')

            field = request.GET.get('field')
            new_value = request.GET.get(field)
            old_value = request.GET.get('old_value')

            DOW = DOW.lower()
            tier_time = tier_time.lower()
            period_label = period_label.lower()

            if product == 'bowling' and center_type == 'experiential':
                product_ids = ProductChoice.retail_bowling_experiential_center
            elif product == 'bowling' and center_type == 'traditional':
                product_ids = ProductChoice.retail_bowling_traditional_center
            elif product == 'shoes':
                product_ids = ProductChoice.retail_shoe_product_ids
            else:
                product_ids = []

            if field == 'time':
                old_value = old_value.lower()
                new_value = new_value.lower()
                # Tracking
                tracking_type_name = 'retail {product} tier schedule change'.format(product=product)
                tracking_type = TrackingType.objects.get(type=tracking_type_name)
                content_type = ContentType.objects.get_for_model(FoodMenuTable)
                input_params = {field: new_value,
                                'old_value': old_value,
                                'center_type': center_type,
                                'product': product,
                                'period_label': period_label,
                                'time': tier_time,
                                'order': order
                                }
                tracking_id = Tracking.objects.create(
                    username=current_user,
                    tracking_type=tracking_type,
                    content_type=content_type,
                    input_params=input_params
                )
                #
                PricingTierTable.objects\
                    .filter(
                        DOW=DOW,
                        time=old_value,
                        period_label=period_label,
                        center_type=center_type,
                        product_id__in=product_ids
                ) \
                    .update(**{
                        field: new_value,
                        'action_user': current_user,
                        'tracking_id': tracking_id
                    })
            else:
                tier = field
                old_value = old_value.replace('$', '')
                new_value = new_value.replace('$', '')

                # Tracking
                tracking_type_name = 'retail {product} tier price change'.format(product=product)
                tracking_type = TrackingType.objects.get(type=tracking_type_name)
                content_type = ContentType.objects.get_for_model(FoodMenuTable)
                input_params = {'price': new_value,
                                'old_value': old_value,
                                'tier': tier,
                                'center_type': center_type,
                                'product': product,
                                'period_label': period_label,
                                'time': tier_time,
                                'order': order
                                }
                tracking_id = Tracking.objects.create(
                    username=current_user,
                    tracking_type=tracking_type,
                    content_type=content_type,
                    input_params=input_params
                )
                #

                PricingTierTable.objects\
                    .filter(
                        DOW=DOW,
                        time=tier_time,
                        period_label=period_label,
                        tier=tier,
                        center_type=center_type,
                        product_id__in=product_ids
                    ) \
                    .update(**{
                        'price': new_value,
                        'action_user': current_user,
                        'tracking_id': tracking_id
                    })

            return JsonResponse({})
