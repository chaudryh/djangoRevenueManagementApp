import io
import json
from io import BytesIO as io
from django.shortcuts import render, HttpResponse

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
from django.views.decorators.csrf import csrf_protect

from RM.Centers.sample.CentersLoadProcessor import *

from DAO.DataDAO import *

# Create your views here.
# from .utils.LoadConfigData import LoadConfigData

EST = pytz.timezone(TIME_ZONE)


@staff_member_required(login_url='/login/')
@csrf_protect
def index(request, *args, **kwargs):
    template_name = 'Centers/CentersIndex.html'
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

        @classmethod
        def get_columns(cls, request, *args, **kwargs):

            columns = \
                [
                    {
                        'field': 'center_id', 'title': 'Id', 'width':50, 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'center_name', 'title': 'Name', 'sortable': True, 'editable': True,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'region', 'title': 'Region', 'sortable': True, 'editable': True,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'district', 'title': 'District', 'sortable': True, 'editable': True,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'sale_region', 'title': 'Sale Region', 'sortable': True, 'editable': True,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'territory', 'title': 'Territory', 'sortable': True, 'editable': True,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': '108', 'title': 'NP Bowl', 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': '110', 'title': 'P Bowl Wk', 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': '111', 'title': 'P Bowl Wknd', 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': '113', 'title': 'Prem Bowl', 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'rvp', 'title': 'RVP', 'sortable': True, 'editable': True,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'food_menu', 'title': 'Food Menu', 'sortable': True, 'editable': True,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'time_zone', 'title': 'TZ', 'sortable': True, 'editable': True,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'address', 'title': 'Address', 'sortable': True, 'editable': True,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'city', 'title': 'City', 'sortable': True, 'editable': True,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'state', 'title': 'State', 'sortable': True, 'editable': True,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'zipcode', 'title': 'Zipcode', 'sortable': True, 'editable': True,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'center_type', 'title': 'Center Type', 'sortable': True, 'editable': True,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'brand', 'title': 'Brand', 'sortable': True, 'editable': True,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'status', 'title': 'Status', 'sortable': True, 'editable': True,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                        # 'filter': {'type': 'select', 'data': ['open', 'closed']}
                    },
                    {
                        'field': 'food_tier', 'title': 'Food Tier', 'sortable': True, 'editable': True,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'alcohol_tier', 'title': 'Alcohol Tier', 'sortable': True, 'editable': True,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                ]

            return JsonResponse({'status': 1, 'msg': '', 'columns': columns})

        @staticmethod
        def create(request, *args, **kwargs):
            page_size = int(request.GET.get('limit'))
            offset = int(request.GET.get('offset'))
            filters = request.GET.get('filter')
            sort = request.GET.get('sort')
            order = request.GET.get('order')

            last_price_from_change = True

            response = DataDAO.get_centers(pagination=True,
                                           page_size=page_size,
                                           offset=offset,
                                           filters=filters,
                                           sort=sort,
                                           order=order,
                                           last_price=True,
                                           last_price_product_ids=ProductChoice.retail_bowling_ids_new_short,
                                           last_price_from_change=last_price_from_change,
                                           as_of_date=UDatetime.now_local().date()
                                          )

            data = response[0]
            num = response[1]

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
        @permission_required('Centers.change_centers', raise_exception=True)
        def edit(request, *args, **kwargs):
            # Tracking
            current_user = request.user

            center_id = request.GET.get('center_id')
            field = request.GET.get('field')
            new_value = request.GET.get(field)

            if field == 'center_type':
                new_value = new_value.lower()
            center_id = center_id.replace('*', '')

            # Tracking
            tracking_type = TrackingType.objects.get(type='center info change')
            content_type = ContentType.objects.get_for_model(Centers)
            input_params = {field: new_value, 'center_id': center_id}
            tracking_id = Tracking.objects.create(
                username=current_user,
                tracking_type=tracking_type,
                content_type=content_type,
                input_params=input_params
            )
            #

            Centers.objects.filter(center_id__exact=center_id)\
                .update(**{
                    field: new_value,
                    'action_user': current_user,
                    'tracking_id': tracking_id
                })

            return JsonResponse({})

        @staticmethod
        def export(request, *args, **kwargs):
            page_size = request.GET.get('limit')
            offset = request.GET.get('offset')
            filters = request.GET.get('filter')
            sort = request.GET.get('sort')
            order = request.GET.get('order')
            file_type = request.GET.get('type')

            pagination = True

            if page_size:
                page_size = int(page_size)
            if offset:
                offset = int(offset)

            columns = [
                       'center_name',
                       'brand',
                       'region',
                       'district',
                       'status',
                       'sale_region',
                       'territory',
                       'rvp',
                       'time_zone',
                       'address',
                       'city',
                       'state',
                       'zipcode',
                       'bowling_tier',
                       'food_tier',
                       'alcohol_tier',
                       'food_menu',
                       'center_type'
                       ]

            data, num = DataDAO.get_centers(pagination=pagination,
                                            page_size=page_size,
                                            offset=offset,
                                            filters=filters,
                                            sort=sort,
                                            order=order,
                                            last_price=True,
                                            last_price_product_ids=ProductChoice.retail_bowling_ids_new_short,
                                            last_price_from_change=True,
                                            lastPriceSplit=True,
                                            columns=columns,
                                            as_of_date=UDatetime.now_local().date()
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
            else:
                response = json.dumps([], ensure_ascii=False)
                response = HttpResponse(response, content_type='application/json')
                response['Content-Disposition'] = 'attachment; filename=export.json'

            return response
