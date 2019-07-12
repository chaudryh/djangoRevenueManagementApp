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

from .processor.CentersLoadProcessor import *

from DAO.DataDAO import *

# Create your views here.
# from .utils.LoadConfigData import LoadConfigData

EST = pytz.timezone(TIME_ZONE)


@staff_member_required(login_url='/login/')
@csrf_protect
def index(request, *args, **kwargs):
    template_name = 'OpenHours/OpenHoursIndex.html'
    return render(request, template_name)


class Panel1:
    class Form1:

        # result_path = os.path.join(BASE_DIR, 'media/RM/Centers/centers.xlsx')

        @classmethod
        def submit(cls, request, *args, **kwargs):
            file_type = request.GET.get('FileType')
            # try:
            if file_type == 'Centers':
                    CentersLoadProcessor.centers_load_processor()
            # except Exception as e:
            #     return JsonResponse({'status': 0, 'msg': e})

            return JsonResponse({'status': 1, 'msg': ''})

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

            response = DataDAO.get_open_hours(pagination=True,
                                              page_size=page_size,
                                              offset=offset,
                                              filters=filters,
                                              sort=sort,
                                              order=order
                                              )

            # print(response)
            data = response[0]
            num = response[1]

            if not data.empty:
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
        @permission_required('OpenHours.change_openhours', raise_exception=True)
        def edit(request, *args, **kwargs):
            center_id = request.GET.get('center_id')
            field = request.GET.get('field')
            new_value = request.GET.get(field)
            DOW = request.GET.get('DOW')

            DOW = DOW.lower()

            OpenHours.objects \
                .filter(center_id__exact=center_id,
                        DOW__exact=DOW,
                        ) \
                .update(**{field: new_value})

            return JsonResponse({})





