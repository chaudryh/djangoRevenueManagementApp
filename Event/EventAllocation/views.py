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
    template_name = 'EventAllocation/EventAllocationIndex.html'
    return render(request, template_name)


class Panel1:
    class Form1:

        # result_path = os.path.join(BASE_DIR, 'media/RM/Centers/centers.xlsx')

        @classmethod
        def submit(cls, request, *args, **kwargs):
            response = Panel2.Table1.get_columns(request=request)
            return response

        @classmethod
        def get_allocation(cls, request, *args, **kwargs):
            selectType = request.GET.get('selectType')
            group = request.GET.get('group')
            subGroup = request.GET.get('subGroup')
            product = request.GET.get('product')
            tier = request.GET.get('tier')

            if selectType == 'group':
                allc_list = EventAllocation.objects.filter().values_list('group', flat=True).distinct()
                allc_list = sorted(allc_list)
            elif selectType == 'subGroup':
                allc_list = EventAllocation.objects.filter(group=group).values_list('subGroup', flat=True).distinct()
                allc_list = sorted(allc_list)
            elif selectType == 'product':
                allc_list = EventAllocation.objects.filter(group=group, subGroup=subGroup)
                allc_list = allc_list.values_list('product', flat=True).distinct()
                allc_list = sorted(allc_list)
            elif selectType == 'tier':
                allc_list = EventAllocation.objects.filter(group=group, subGroup=subGroup)
                allc_list = allc_list.filter(product=product).values_list('tier', flat=True).distinct()
                allc_list = ['All'] + list(allc_list)
            else:
                return JsonResponse({'status': 1, 'msg': '', 'results': []})

            result = \
            [
                {
                    'id': item,
                    "text": item,
                }
                for item in allc_list
            ]

            return JsonResponse({'status': 1, 'msg': '', 'results': result})

        @classmethod
        def get_allocation_old(cls, request, *args, **kwargs):
            search = request.GET.get('search')
            if search:
                allc_obj = EventAllocation.objects \
                    .filter(Q(category__contains=search) | Q(product__contains=search))
            else:
                allc_obj = EventAllocation.objects.all()

            if not allc_obj.exists():
                return JsonResponse({'status': 1, 'msg': '', 'results': []})

            allc_records = pd.DataFrame.from_records(allc_obj.values('row_id',
                                                                     'category_id',
                                                                     'group',
                                                                     'category',
                                                                     'product'
                                                                     ))
            allc_records.drop_duplicates(subset=['category', 'product'], inplace=True)
            allc_records['category_product'] = allc_records['category'] + ':' + allc_records['product']
            allc_records['category_product'] = allc_records[['row_id', 'category_product']].values.tolist()
            allc_dict = allc_records.groupby('group')['category_product'].apply(lambda x: x.tolist()).to_dict()

            result = \
                [
                    {
                        "text": k1,
                        "children": [
                            {
                                "id": v2[0],
                                "text": v2[1]
                            }
                            for v2 in v1
                        ]
                    }
                    for k1, v1 in allc_dict.items()
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
            product = request.GET.get('product')
            tier = request.GET.get('tier')

            sub_products = EventAllocation.objects.filter(group=group, subGroup=subGroup)
            if tier and tier != 'All':
                sub_products = sub_products.filter(tier=tier)

            sub_products = sub_products \
                .filter(product=product) \
                .values_list('subProduct', flat=True) \
                .distinct()

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
                        'field': sub_product,
                        'title': sub_product,
                        'editable': True,
                        'align': 'center',
                        'vlign': 'center',
                    }
                    for sub_product in sub_products
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
            product = request.GET.get('product')
            tier = request.GET.get('tier')

            data, num = GetEvent.get_event_allocation(group, subGroup, product, tier,
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
        @permission_required('Models.change_eventallocation', raise_exception=True)
        def edit(request, *args, **kwargs):

            current_user = request.user
            report_type = request.GET.get('product')
            order = request.GET.get('order')

            field = request.GET.get('field')
            new_value = request.GET.get(field)
            old_value = request.GET.get('old_value')
            subProduct = field

            group = request.GET.get('group')
            subGroup = request.GET.get('subGroup')
            product = request.GET.get('product')
            tier = request.GET.get('tier')

            old_value = old_value.replace('$', '')
            new_value = new_value.replace('$', '')

            # Tracking
            tracking_type_name = 'retail bowling tier price change'
            tracking_type = TrackingType.objects.get(type=tracking_type_name)
            content_type = ContentType.objects.get_for_model(ProductPrice)
            input_params = {'price': new_value,
                            'old_value': old_value,
                            'group': group,
                            'subGroup': subGroup,
                            'product': product,
                            'subProduct': subProduct,
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
            allocationObj = EventAllocation.objects.filter(tier=tier, group=group, subGroup=subGroup,
                                                           product=product, subProduct=subProduct)

            allocationObj \
                .update(**{
                    'price': new_value,
                    'action_user': current_user,
                    'tracking_id': tracking_id
                })

            return JsonResponse({})
