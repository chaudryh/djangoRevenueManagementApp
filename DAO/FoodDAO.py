import pandas as pd
import pytz
import ast
from datetime import datetime as dt, timedelta as td

from django.db.models import Q, Count, Min, Max, Sum, Avg, Value
from django.db.models.functions import Concat
from django.core.paginator import Paginator
import operator
from functools import reduce

from bowlero_backend.settings import TIME_ZONE

from Food.FoodByCenter.models.models import *
from Food.FoodChangeReport.models.models import FoodChangeReport

EST = pytz.timezone(TIME_ZONE)


class FoodDataDao:
    @classmethod
    def getFoodByCenter(cls, menu_id, date, category, district, region, center_id,
                        pagination=False, page_size=None, offset=None, filters=None, sort=None, order=None,
                        onlyPrice=False, download=False):

        if sort and order:
            # if sort == 'OLD':
            #     sort = 'create_date'
            # elif sort == 'balance_hour':
            #     sort = 'estimate_hour'
            if order == 'desc':
                sort = '-' + sort
        else:
            sort = ''

        price_objs = FoodPrice.objects \
            .filter(menu_id=menu_id, status='active') \
            .exclude(Q(start__gt=date) | Q(end__lt=date))

        # Filter by centers and food categories
        if category:
            price_objs = price_objs.filter(category__in=category)
        if district:
            price_objs = price_objs.filter(center_id__district__in=district)
        if region:
            price_objs = price_objs.filter(center_id__region__in=region)
        if center_id:
            price_objs = price_objs.filter(center_id__center_id__in=center_id)

        if filters:
            filters = ast.literal_eval(filters)

            for key, value in filters.items():
                filters_list = value.split(',')
                filters_list = [x.strip() for x in filters_list]
                filters[key] = filters_list
            if filters.get('food'):
                filter_item = filters.get('food')
                if len(filter_item) == 1:
                    price_objs = price_objs.filter(product__product_name__icontains=filter_item[0])
                else:
                    price_objs = price_objs.filter(reduce(operator.or_, (Q(product__product_name__icontains=item)
                                                                         for item in filter_item if item)))
            if filters.get('product_num'):
                filter_item = filters.get('product_num')
                if len(filter_item) == 1:
                    price_objs = price_objs.filter(product__product_id__icontains=filter_item[0])
                else:
                    price_objs = price_objs.filter(product__product_id__in=filter_item)

        # num = price_objs.count()
        # if pagination:
        #     paginator = Paginator(price_objs, page_size, )
        #     current_page = int(offset / page_size) + 1
        #     price_objs = paginator.page(current_page).object_list

        price_record = pd.DataFrame.from_records(price_objs.values(
            'price',
            'product__product_id',
            'product__product_name',
            'menu__menu_id',
            'menu__menu_name',
            'center_id',
            'center_id__center_name',
            'category',
            'start',
            'end',
            'action_time',
            'status'
        ))

        if price_record.empty:
            return pd.DataFrame(), 0

        price_record.rename({
            'product__product_id': 'product_num',
            'product__product_name': 'food',
            'menu__menu_id': 'menu_id',
            'menu__menu_name': 'menu',
            'center_id__center_name': 'center_name',
        }, axis=1, inplace=True)

        if onlyPrice:
            return price_record, 0

        price_record = price_record \
            .sort_values(['center_id', 'menu', 'category', 'product_num', 'action_time']) \
            .drop_duplicates(['center_id', 'menu', 'category', 'product_num'], keep='last')

        if download:
            center_id_name = {int(row['center_id']): row['center_id'] + '-' + row['center_name']
                              for index, row in price_record.iterrows()}
            price_record['center_id'] = price_record['center_id'].astype(int)
        else:
            center_id_name = {}

        price_record = pd.pivot_table(price_record,
                                      index=['food', 'product_num', 'menu', 'category'],
                                      columns=['center_id'],
                                      values=['price'],
                                      aggfunc='first',
                                      fill_value=None)

        price_record.columns = price_record.columns.droplevel(0)
        price_record.columns.name = None
        price_record.reset_index(inplace=True)

        num = len(price_record)
        # print(price_record)

        if download:
            price_record.rename(center_id_name, axis=1, inplace=True)

        return price_record, num

    @classmethod
    def updateFoodPrice(cls, menu_id, category_products, centers, start, end, price, category, user, tracking_id):

        # Get all historical price records
        separator = '---'
        old_prices = FoodPrice.objects \
            .annotate(
                category_product=Concat('category', Value(separator), 'product')
            ) \
            .filter(
                menu=menu_id,
                center_id__in=centers,
                status='active',
                category_product__in=['{}{}{}'.format(category, separator, product) for category, product in category_products]
            )

        if start and end:
            old_prices = old_prices.exclude(Q(start__gt=end) | Q(end__lt=start))
        elif start:
            old_prices = old_prices.exclude(Q(end__lt=start))
        elif end:
            old_prices = old_prices.exclude(Q(start__gt=end))

        old_prices_records = pd.DataFrame.from_records(old_prices.values())

        # Add new prices
        price_records, num = cls.getFoodByCenter(menu_id, start, category, None, None, centers, onlyPrice=True)

        if not price_records.empty:
            price_records = price_records \
                .sort_values(['center_id', 'menu', 'category', 'product_num', 'action_time']) \
                .drop_duplicates(['center_id', 'menu', 'category', 'product_num'], keep='last')
            # Filter by selections
            price_records['category_product'] = price_records['category'] + '---' + price_records['product_num']
            price_records = price_records[price_records['category_product'].isin(['{}---{}'.format(category, product)
                                                                         for category, product in category_products])]
        else:
            price_records = pd.DataFrame(columns=['center_id', 'menu_id', 'category', 'product_num'])

        food_menu = Menu.objects.get(menu_id=menu_id)
        for center in centers:
            center_obj = Centers.objects.get(center_id=center)
            for category_product in category_products:
                category, product_id = category_product
                product = Product.objects.get(product_id=product_id)
                row = price_records[
                    (price_records['center_id'] == str(center)) &
                    (price_records['menu_id'] == int(menu_id)) &
                    (price_records['category'] == category) &
                    (price_records['product_num'] == product_id)
                ]

                if row.empty:
                    price_old = None
                    price_new = cls.price_converter(None, price['price_symbol'], price['price'], price['unit'])
                else:
                    price_old = row['price'].values[0]
                    price_new = cls.price_converter(price_old, price['price_symbol'], price['price'], price['unit'])

                tracking_obj = Tracking.objects.get(tracking_id=tracking_id)
                FoodPrice.objects.create(product=product,
                                         center_id=center_obj,
                                         menu=food_menu,
                                         category=category,
                                         price=price_new,
                                         start=start,
                                         end=end,
                                         action_user=user,
                                         tracking_id=tracking_obj
                                         )

                # Tracking Change Report
                description = 'Change food "{food}" in menu "{menu}" category "{category}" price from "${price_old}" to "${price_new}"'\
                    .format(food=product_id, menu=food_menu.menu_name, category=category,
                            price_old=price_old, price_new=price_new)

                FoodChangeReport.objects \
                    .create\
                        (
                            tracking_id=tracking_obj,
                            username=user,
                            center_id=center_obj,
                            product_id=product,
                            category=category,
                            menu_id2=food_menu,
                            description=description,
                            price_old=price_old,
                            price_new=price_new,
                            product_start=start,
                            product_end=end
                        )

        # Revise old prices
        for index, row in old_prices_records.iterrows():
            start_old, end_old = row['start'], row['end']
            start_old = None if str(start_old) == 'NaT' or not start_old else start_old.date()
            end_old = None if str(end_old) == 'NaT' or not end_old else end_old.date()
            price_obj = FoodPrice.objects.get(id=row['id'])

            if start_old and not end_old and start and not end:
                if start_old >= start:
                    price_obj.status = 'inactive'
                else:
                    price_obj.end = max(end - td(days=1), start_old)
                price_obj.save()
            elif start_old and end_old and start and end:
                if start <= start_old <= end_old <= end:
                    price_obj.status = 'inactive'
                elif start <= start_old <= end <= end_old:
                    price_obj.start = min(end + td(days=1), end_old)
                elif start_old <= start <= end_old <= end:
                    price_obj.end = max(start - td(days=1), start_old)
                price_obj.save()
            elif start_old and not end_old and start and end:
                if start <= start_old <= end:
                    price_obj.start = end + td(days=1)
                price_obj.save()

    @classmethod
    def price_converter(cls, price_base, price_symbol, price_change, price_unit, ndigits=2):
        price_new = None
        if not price_base:
            price_base = 0

        if price_symbol == 'equal':
            if price_unit == 'dollar':
                price_new = price_change
            elif price_unit == 'percent':
                price_new = price_base * price_change / 100

        if price_symbol == 'plus':
            if price_unit == 'dollar':
                price_new = price_base + price_change
            elif price_unit == 'percent':
                price_new = price_base + price_change * price_base / 100

        if price_symbol == 'minus':
            if price_unit == 'dollar':
                price_new = price_base - price_change
            elif price_unit == 'percent':
                price_new = price_base - price_change * price_base / 100

        price_new = round(price_new, ndigits)
        return price_new
