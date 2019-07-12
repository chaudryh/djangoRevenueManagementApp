import os
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

from utils.UTable import UTable

# Create your views here.
# from .utils.LoadConfigData import LoadConfigData

EST = pytz.timezone(TIME_ZONE)


@staff_member_required(login_url='/login/')
@csrf_protect
def index(request, *args, **kwargs):
    template_name = 'Food/FoodIndex.html'
    return render(request, template_name)


class Panel1:
    class Form1:

        # result_path = os.path.join(BASE_DIR, 'media/RM/Centers/centers.xlsx')

        @classmethod
        def submit(cls, request, *args, **kwargs):
            date = request.GET.get('date')
            food_menu = request.GET.get('food_menu')

            date = UDatetime.datetime_str_init(date)
            if not food_menu:
                food_menu = 'FY19 Bowled'

            food_tiers = MenuTier.objects\
                .filter(
                    menu__name=food_menu,
                    status='active'
                ) \
                .values_list('tier', flat=True)
            food_tiers = [(food_tier.capitalize(), food_tier.lower()) for food_tier in food_tiers]
            food_tiers.sort()

            columns = \
                [
                    {
                        'field': 'state', 'title': 'State', 'checkbox': True
                    },
                    {
                        'field': 'food', 'title': 'Food', 'sortable': True, 'editable': True,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'menu', 'title': 'Menu', 'sortable': True, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'category', 'title': 'Category', 'sortable': True, 'editable': True,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'product_num', 'title': 'Prod Num', 'sortable': True, 'editable': True,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'start', 'title': 'Start', 'sortable': True, 'editable': True,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'end', 'title': 'End', 'sortable': True, 'editable': True,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'product_id', 'title': 'product_id', 'visible': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                    {
                        'field': 'menu_id', 'title': 'menu_id', 'visible': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                    },
                ]

            columns += [
                {
                    'field': tier[1],
                    'title': tier[0],
                    'editable': True,
                    'align': 'center',
                    'vlign': 'center',
                }
                for tier in food_tiers
            ]

            return JsonResponse({'status': 1, 'msg': '', 'columns': columns})

        @classmethod
        def get_food_menu(cls, request, *args, **kwargs):

            menu_list = Menu.objects \
                .filter(status='active') \
                .values_list('name', flat=True) \
                .order_by('name')

            result = \
                [
                    {
                        "id": menu,
                        "text": menu
                    }
                    for menu in menu_list
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

        @staticmethod
        def create(request, *args, **kwargs):
            page_size = int(request.GET.get('limit'))
            offset = int(request.GET.get('offset'))
            filters = request.GET.get('filter')
            sort = request.GET.get('sort')
            order = request.GET.get('order')
            date = request.GET.get('date')
            food_menu = request.GET.get('food_menu')

            if not food_menu:
                food_menu = 'FY19 Bowled'

            data, num = DataDAO.get_food(
                                         date=date,
                                         food_menu=food_menu,
                                         pagination=True,
                                         page_size=page_size,
                                         offset=offset,
                                         filters=filters,
                                         sort=sort,
                                         order=order,
                                         )

            if not data.empty:
                data = data.where((pd.notnull(data)), "-")

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
        @permission_required('Food.change_foodmenutable', raise_exception=True)
        def edit(request, *args, **kwargs):

            current_user = request.user
            food = request.GET.get('food')
            menu = request.GET.get('menu')
            product_id = request.GET.get('product_id')
            menu_id = request.GET.get('menu_id')
            category = request.GET.get('category')
            field = request.GET.get('field')
            new_value = request.GET.get(field)
            old_value = request.GET.get('old_value')

            menu_obj = Menu.objects.get(menu_id=menu_id)
            product_obj = Product.objects.get(product_id=product_id)

            if 'tier' in field or 'Tier' in field:
                if new_value:
                    new_value = new_value.replace('$', '')
                    if new_value in ['-', '']:
                        new_value = None
                else:
                    new_value = None

                if old_value:
                    old_value = old_value.replace('$', '')
                    if old_value in ['-', '']:
                        old_value = None
                else:
                    old_value = None

                # Tracking
                tracking_type = TrackingType.objects.get(type='retail food tier price change')
                content_type = ContentType.objects.get_for_model(FoodMenuTable)
                input_params = {field: new_value}
                tracking_id = Tracking.objects.create(
                    username=current_user,
                    tracking_type=tracking_type,
                    content_type=content_type,
                    input_params=input_params
                )
                #
                FoodMenuTable.objects \
                    .update_or_create(
                        product=product_obj,
                        menu=menu_obj,
                        category=category,
                        tier=field.lower(),
                        defaults={
                            'price': new_value,
                            'status': 'active',
                            'action_user': current_user,
                            'tracking_id': tracking_id
                        }
                    )

                # Tracking Change Report
                description = 'Change food "{food}" in menu "{menu}" tier "{tier}" price from "${price_old}" to "${price_new}"'\
                    .format(food=food, menu=menu, tier=field, price_old=old_value, price_new=new_value)

                menu_obj = Menu.objects.get(menu_id=menu_id)
                product_obj = Product.objects.get(product_id=product_id)
                FoodChangeReport.objects \
                    .update_or_create\
                        (
                            tracking_id=tracking_id,
                            username=current_user,
                            action_time=UDatetime.now_local(),
                            product_id=product_obj,
                            menu_id=menu_obj,
                            tier=field,
                            description=description,
                            price_old=old_value,
                            price_new=new_value
                        )

            elif field == 'food':

                # Tracking
                tracking_type = TrackingType.objects.get(type='retail food name change')
                content_type = ContentType.objects.get_for_model(Product)
                input_params = {field: new_value}
                tracking_id = Tracking.objects.create(
                    username=current_user,
                    tracking_type=tracking_type,
                    content_type=content_type,
                    input_params=input_params
                )
                #

                Product.objects \
                    .filter(product_id=product_id) \
                    .update(**{
                        'product_name': new_value,
                        'action_user': current_user,
                        'tracking_id': tracking_id
                    })

                # Tracking Change Report
                description = 'Change food name from {food_old} to {food_new} in menu {menu}'\
                    .format(food_old=old_value, food_new=new_value, menu=menu)

                FoodChangeReport.objects \
                    .update_or_create\
                        (
                            tracking_id=tracking_id,
                            username=current_user,
                            action_time=UDatetime.now_local(),
                            product_id=product_obj,
                            menu_id=menu_obj,
                            description=description,
                        )

            elif field == 'category':

                # Tracking
                tracking_type = TrackingType.objects.get(type='retail food category change')
                content_type = ContentType.objects.get_for_model(FoodMenuTable)
                input_params = {field: new_value}
                tracking_id = Tracking.objects.create(
                    username=current_user,
                    tracking_type=tracking_type,
                    content_type=content_type,
                    input_params=input_params
                )
                #

                FoodMenuTable.objects \
                    .filter(product__product_id=product_id, menu__menu_id=menu_id, category=old_value) \
                    .update(**{
                        field: new_value,
                        'action_user': current_user,
                        'tracking_id': tracking_id
                    })

                # Tracking Change Report
                description = 'Change food {food} in menu {menu} category from {category_old} to {category_new}'\
                    .format(food=food, menu=menu, category_old=old_value, category_new=new_value)

                FoodChangeReport.objects \
                    .update_or_create \
                        (
                            tracking_id=tracking_id,
                            username=current_user,
                            action_time=UDatetime.now_local(),
                            product_id=product_obj,
                            menu_id=menu_obj,
                            category=new_value,
                            description=description,
                        )

            elif field == 'product_num':

                # Tracking
                tracking_type = TrackingType.objects.get(type='retail food name change')
                content_type = ContentType.objects.get_for_model(Product)
                input_params = {field: new_value}
                tracking_id = Tracking.objects.create(
                    username=current_user,
                    tracking_type=tracking_type,
                    content_type=content_type,
                    input_params=input_params
                )
                #

                Product.objects \
                    .filter(product_id=product_id) \
                    .update(**{
                        'product_num': new_value,
                        'action_user': current_user,
                        'tracking_id': tracking_id
                    })

                # Tracking Change Report
                description = 'Change food {food} in menu {menu} {field} from {old_value} to {new_value}'\
                    .format(food=food, menu=menu, field=field, old_value=old_value, new_value=new_value)

                FoodChangeReport.objects \
                    .update_or_create\
                        (
                            tracking_id=tracking_id,
                            username=current_user,
                            action_time=UDatetime.now_local(),
                            product_id=product_obj,
                            menu_id=menu_obj,
                            description=description,
                        )

            return JsonResponse({})

    class Modal1Food:

        @staticmethod
        @permission_required('Food.change_foodmenutable', raise_exception=True)
        def add(request, *args, **kwargs):
            current_user = request.user

            product_name = request.GET.get('add_food_product_name')
            menu = request.GET.get('add_food_menu')
            category = request.GET.get('add_food_category')
            product_num = request.GET.get('add_food_product_num')
            start = request.GET.get('add_food_start')
            end = request.GET.get('add_food_end')

            # Tracking
            tracking_type = TrackingType.objects.get(type='retail food remove food')
            content_type = ContentType.objects.get_for_model(FoodMenuTable)
            input_params = {'product_name': product_name, 'menu': menu, 'category': category,
                            'product_num': product_num, 'start': start, 'end': end}
            tracking_id = Tracking.objects.create(
                username=current_user,
                tracking_type=tracking_type,
                content_type=content_type,
                input_params=input_params
            )
            #

            # add product
            # product_obj = Product.objects.filter(product_name=product_name, )
            # if product_obj.exists():
            #     product_obj.update(
            #         status='active',
            #         action_user=current_user,
            #         action_time=UDatetime.now_local()
            #     )
            #     product_obj = product_obj[0]
            # else:
            # Auto assign product id
            if product_num:
                product_id = product_num
            else:
                product_id_list = Product.objects \
                    .exclude(report_type='Event')\
                    .extra(select={'product_id': 'CAST(product_id AS INTEGER)'}) \
                    .order_by('-product_id') \
                    .values_list('product_id', flat=True)

                product_id_list = [i for i in product_id_list if i >= 10000 and i<20000]
                if product_id_list:
                    product_id = max(product_id_list) + 1
                else:
                    product_id = 10000

            product_obj = Product.objects.create(
                product_id=product_id,
                product_name=product_name,
                readable_product_name=product_name,
                short_product_name=product_name,
                product_num=product_num,
                status='active',

                action_user=current_user,
                action_time=UDatetime.now_local()
            )

            # add to FoodMenuTable
            menu_obj = Menu.objects.get(name=menu)
            tiers = MenuTier.objects.filter(menu=menu_obj).values_list('tier', flat=True)
            if not tiers:
                tiers = ['tier 1']
            FoodMenuTable.objects.update_or_create(
                product=product_obj,
                menu=menu_obj,
                category=category,
                tier=tiers[0],
                price=0,
                defaults={
                    'status': 'active',
                    'action_user': current_user,
                    'action_time': UDatetime.now_local()
                }
            )

            # add product schedule
            if start or end:
                if start:
                    start = UDatetime.datetime_str_init(start)
                else:
                    start = None
                if end:
                    end = UDatetime.datetime_str_init(end)
                else:
                    end = None
                ProductSchedule.objects.update_or_create(
                    product_id=product_obj,
                    defaults={
                        'start': start,
                        'end': end,
                        'status': 'active',
                        'product_name': product_obj.product_name,
                        'action_user': current_user,
                        'action_time': UDatetime.now_local()
                    }
                )

            # Tracking Change Report
            description = 'Add food {food} in menu {menu}'.format(food=product_name, menu=menu)
            if start:
                description += ' start from {start}'.format(start=start)
            if end:
                description += ' to {end}'.format(end=end)
            menu_obj = Menu.objects.get(name=menu)
            product_obj = Product.objects.get(product_id=product_id)

            food_change_report, exist = FoodChangeReport.objects \
                .update_or_create \
                    (
                        tracking_id=tracking_id,
                        username=current_user,
                        action_time=UDatetime.now_local(),
                        product_id=product_obj,
                        menu_id=menu_obj,
                        description=description,
                    )
            if start:
                food_change_report.product_start = start
                food_change_report.save()
            if end:
                food_change_report.product_end = end
                food_change_report.save()

            return JsonResponse({'status': 1, 'msg': ''})

        @staticmethod
        @permission_required('Food.change_foodmenutable', raise_exception=True)
        def delete(request, *args, **kwargs):
            current_user = request.user

            selections = request.GET.get('selections')
            selections = json.loads(selections)

            # Tracking
            tracking_type = TrackingType.objects.get(type='retail food remove food')
            content_type = ContentType.objects.get_for_model(FoodMenuTable)
            input_params = {'selections': selections}
            tracking_id = Tracking.objects.create(
                username=current_user,
                tracking_type=tracking_type,
                content_type=content_type,
                input_params=input_params
            )
            #

            for selection in selections:
                product = selection['food']
                menu = selection['menu']
                product_id = selection['product_id']
                menu_id = selection['menu_id']
                menu_obj = Menu.objects.get(menu_id=menu_id)
                product_obj = Product.objects.get(product_id=product_id)

                FoodMenuTable.objects \
                    .filter(
                        product_id__product_id=product_id,
                        menu__menu_id=menu_id,
                    ) \
                    .update(
                        status='inactive',
                        action_user=current_user,
                        action_time=UDatetime.now_local()
                    )

                # Tracking Change Report
                description = 'Remove food {food} in menu {menu}'.format(food=product, menu=menu)

                FoodChangeReport.objects \
                    .update_or_create \
                        (
                            tracking_id=tracking_id,
                            username=current_user,
                            action_time=UDatetime.now_local(),
                            product_id=product_obj,
                            menu_id=menu_obj,
                            description=description
                        )

            return JsonResponse({'status': 1, 'msg': ''})

    class Modal2Menu:

        @staticmethod
        @permission_required('Food.change_foodmenutable', raise_exception=True)
        def add(request, *args, **kwargs):
            current_user = request.user

            menu = request.GET.get('add_menu_name')
            copy_from = request.GET.get('copy_from')

            # Tracking
            tracking_type = TrackingType.objects.get(type='retail food add menu')
            content_type = ContentType.objects.get_for_model(Menu)
            input_params = {'menu': menu, 'copy_from': copy_from}
            tracking_id = Tracking.objects.create(
                username=current_user,
                tracking_type=tracking_type,
                content_type=content_type,
                input_params=input_params
            )
            #

            Menu.objects.update_or_create(
                name=menu,
                defaults={
                    'status': 'active',

                    'action_user': current_user,
                    'action_time': UDatetime.now_local(),
                    'tracking_id': tracking_id
                }
            )

            # Tracking Change Report
            description = 'Add new menu {menu}'.format(menu=menu)
            if copy_from:
                description += ' copy from menu {copy_from}'.format(copy_from=copy_from)
            menu_obj = Menu.objects.get(name=menu)

            FoodChangeReport.objects \
                .update_or_create \
                    (
                        tracking_id=tracking_id,
                        username=current_user,
                        action_time=UDatetime.now_local(),
                        menu_id=menu_obj,
                        description=description
                )

            return JsonResponse({'status': 1, 'msg': ''})

        @staticmethod
        @permission_required('Food.change_foodmenutable', raise_exception=True)
        def edit(request, *args, **kwargs):
            current_user = request.user

            menu_old = request.GET.get('edit_old_menu_name')
            menu_new = request.GET.get('edit_new_menu_name')

            # Tracking
            tracking_type = TrackingType.objects.get(type='retail food change menu name')
            content_type = ContentType.objects.get_for_model(Menu)
            input_params = {'menu_old': menu_old, 'menu_new': menu_new}
            tracking_id = Tracking.objects.create(
                username=current_user,
                tracking_type=tracking_type,
                content_type=content_type,
                input_params=input_params
            )
            #

            Menu.objects\
                .filter(name=menu_old) \
                .update(
                    name=menu_new,
                    action_user=current_user,
                    action_time=UDatetime.now_local(),
                    tracking_id= tracking_id
                )

            # Tracking Change Report
            description = 'Rename menu {menu_old} to {menu_new}'.format(menu_old=menu_old, menu_new=menu_new)
            menu_obj = Menu.objects.get(name=menu_new)

            FoodChangeReport.objects \
                .update_or_create \
                    (
                        tracking_id=tracking_id,
                        username=current_user,
                        action_time=UDatetime.now_local(),
                        menu_id=menu_obj,
                        description=description
                )

            return JsonResponse({'status': 1, 'msg': ''})

        @staticmethod
        @permission_required('Food.change_foodmenutable', raise_exception=True)
        def delete(request, *args, **kwargs):
            current_user = request.user

            menu = request.GET.get('delete_menu_name')

            # Tracking
            tracking_type = TrackingType.objects.get(type='retail food delete menu')
            content_type = ContentType.objects.get_for_model(Menu)
            input_params = {'menu': menu}
            tracking_id = Tracking.objects.create(
                username=current_user,
                tracking_type=tracking_type,
                content_type=content_type,
                input_params=input_params
            )
            #

            Menu.objects\
                .filter(name=menu) \
                .update(
                    status='inactive',
                    action_user=current_user,
                    action_time=UDatetime.now_local(),
                    tracking_id=tracking_id
                )

            # Tracking Change Report
            description = 'Delete menu {menu}'.format(menu=menu)
            menu_obj = Menu.objects.get(name=menu)

            FoodChangeReport.objects \
                .update_or_create\
                    (
                        tracking_id=tracking_id,
                        username=current_user,
                        action_time=UDatetime.now_local(),
                        menu_id=menu_obj,
                        description=description
                    )

            return JsonResponse({'status': 1, 'msg': ''})

    class Modal3Tier:

        @staticmethod
        @permission_required('Food.change_foodmenutable', raise_exception=True)
        def add(request, *args, **kwargs):
            current_user = request.user

            tier_name = request.GET.get('add_tier_name')
            copy_from = request.GET.get('add_tier_copy_from')
            menu = request.GET.get('add_tier_menu')

            # Tracking
            tracking_type = TrackingType.objects.get(type='retail food add tier')
            content_type = ContentType.objects.get_for_model(MenuTier)
            input_params = {'tier': tier_name, 'menu': menu, 'copy_from': copy_from}
            tracking_id = Tracking.objects.create(
                username=current_user,
                tracking_type=tracking_type,
                content_type=content_type,
                input_params=input_params
            )
            #

            menu_obj = Menu.objects.get(name=menu)
            MenuTier.objects.update_or_create(
                menu=menu_obj,
                tier=tier_name,
                defaults={
                    'status': 'active',
                    'action_user': current_user,
                    'action_time': UDatetime.now_local(),
                    'tracking_id': tracking_id
                }
            )

            # Tracking Change Report
            description = 'Add New tier {tier_name} in menu {menu}'.format(tier_name=tier_name, menu=menu)
            if copy_from:
                description += ' copy from menu {menu}'.format(menu=menu)

            FoodChangeReport.objects \
                .update_or_create\
                    (
                        tracking_id=tracking_id,
                        username=current_user,
                        action_time=UDatetime.now_local(),
                        menu_id=menu_obj,
                        tier=tier_name,
                        description=description
                    )

            return JsonResponse({'status': 1, 'msg': ''})

        @staticmethod
        @permission_required('Food.change_foodmenutable', raise_exception=True)
        def edit(request, *args, **kwargs):
            current_user = request.user

            tier_old = request.GET.get('edit_tier_name_old')
            tier_new = request.GET.get('edit_tier_name_new')
            menu = request.GET.get('edit_tier_menu')

            tier_old = tier_old.lower()
            tier_new = tier_new.lower()

            menu_tier_obj = MenuTier.objects.filter(tier=tier_old)
            food_menu_obj = FoodMenuTable.objects.filter(tier=tier_old)

            # Tracking
            tracking_type = TrackingType.objects.get(type='retail food change tier name')
            content_type = ContentType.objects.get_for_model(FoodMenuTable)
            input_params = {'tier_old': tier_old, 'tier_new': tier_new, 'menu': menu}
            tracking_id = Tracking.objects.create(
                username=current_user,
                tracking_type=tracking_type,
                content_type=content_type,
                input_params=input_params
            )
            #

            if menu:
                menu_tier_obj = menu_tier_obj.filter(
                    menu__name=menu,
                )
                food_menu_obj = food_menu_obj.filter(
                    menu__name=menu,
                )

            if menu_tier_obj.exists():
                menu_tier_obj.update(
                    tier=tier_new,
                    action_user=current_user,
                    action_time=UDatetime.now_local(),
                    tracking_id=tracking_id
                )

            if food_menu_obj.exists():
                food_menu_obj.update(
                    tier=tier_new,
                    action_user=current_user,
                    action_time=UDatetime.now_local(),
                    tracking_id=tracking_id
                )

            # Tracking Change Report
            description = 'Rename tier {tier_old} to {tier_new}'.format(tier_old=tier_old,
                                                                                        tier_new=tier_new
                                                                                        )
            if menu:
                description += ' in menu {menu}'.format(menu=menu)

            menu_obj = Menu.objects.get(name=menu)
            FoodChangeReport.objects \
                .update_or_create\
                    (
                        tracking_id=tracking_id,
                        username=current_user,
                        action_time=UDatetime.now_local(),
                        menu_id=menu_obj,
                        tier=tier_old,
                        description=description
                    )

            return JsonResponse({'status': 1, 'msg': ''})

        @staticmethod
        @permission_required('Food.change_foodmenutable', raise_exception=True)
        def delete(request, *args, **kwargs):
            current_user = request.user

            tier_name = request.GET.get('delete_tier_name')
            menu = request.GET.get('delete_tier_menu')

            tier_name = tier_name.lower()

            # Tracking
            tracking_type = TrackingType.objects.get(type='retail food delete tier')
            content_type = ContentType.objects.get_for_model(MenuTier)
            input_params = {'tier': tier_name, 'menu': menu}
            tracking_id = Tracking.objects.create(
                username=current_user,
                tracking_type=tracking_type,
                content_type=content_type,
                input_params=input_params
            )
            #

            MenuTier.objects \
                .filter(tier=tier_name, menu__name=menu) \
                .update(
                    status='inactive',
                    action_user=current_user,
                    action_time=UDatetime.now_local(),
                    tracking_id=tracking_id
                )

            # Tracking Change Report
            description = 'Delete tier {tier_name} in menu {menu}'.format(tier_name=tier_name, menu=menu)
            menu_obj = Menu.objects.get(name=menu)
            FoodChangeReport.objects \
                .update_or_create\
                    (
                        tracking_id=tracking_id,
                        username=current_user,
                        action_time=UDatetime.now_local(),
                        menu_id=menu_obj,
                        tier=tier_name,
                        description=description
                    )

            return JsonResponse({'status': 1, 'msg': ''})