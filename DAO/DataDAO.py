import numpy as np
import pandas as pd
import pytz
import ast
import itertools
import re

from datetime import datetime as dt, timedelta as td
from dateutil.parser import parse
from dateutil.tz import tzlocal
from django.db.models import Q, Count, Min, Max, Sum, Avg
import operator
from functools import reduce
from django.db.models.functions import Concat
from django.core.paginator import Paginator
from django.utils.html import strip_tags
from bowlero_backend.settings import TIME_ZONE

from RM.Centers.models.models import *
from RM.Pricing.models.models import *
from RM.Food.models.models import *
from Models.models.models import *
from Alcohol.Alcohol.models.models import *
from Alcohol.AlcoholChangeReport.models.models import *
from Weather.Weather.models.models import *
from Email.EmailNotice.models.models import *
from BowlingShoe.BSChangeReport.models.models import *
from Food.FoodChangeReport.models.models import *
from Event.EventChangeReport.models.models import *
from utils.UDatetime import UDatetime

from api.AcisAPI import AcisAPI

EST = pytz.timezone(TIME_ZONE)


class ProductOptGet:

    @classmethod
    def get_productopt(cls, product_ids, start, end, center_ids=None):

        productopt_obj = ProductOpt.objects \
            .filter(product_id__in=product_ids
                    ) \
            .exclude(Q(start__gt=end) |
                     Q(end__lt=start)
                     )

        if center_ids:
            productopt_obj = productopt_obj.filter(center_id__in=center_ids)

        productopt_records = pd.DataFrame.from_records(productopt_obj.values('center_id',
                                                                             'product_id',
                                                                             'opt',
                                                                             'start',
                                                                             'end',
                                                                             'action_time'
                                                                             ))

        if productopt_records.empty:
            return pd.DataFrame()

        productopt_records.sort_values(['action_time'], inplace=True)
        # print(productopt_records)
        date_range = UDatetime.date_range(start, end)
        if not center_ids:
            center_ids = Centers.objects.filter(status='open').values_list('center_id', flat=True)

        result_list = [
            {'center_id': center_id, 'product_id': product_id, 'date': date, 'opt': None}
            for center_id in center_ids
            for product_id in product_ids
            for date in date_range
        ]

        result_records = pd.DataFrame(result_list)
        # result_records['date'] = pd.to_datetime(result_records['date'])
        # result_records.loc[result_records['product_id'].isin(ProductChoice.products_always_opt_in), 'opt'] = 'In'

        for index, row in productopt_records.iterrows():
            start_row = row['start']
            end_row = row['end']
            if not start_row:
                start_row = start
            if not end_row:
                end_row = end

            result_records \
                .loc[(result_records['date'] >= start_row) &
                     (result_records['date'] <= end_row) &
                     (result_records['center_id'] == row['center_id']) &
                     (result_records['product_id'] == row['product_id']), 'opt'] \
                = row['opt']

        return result_records

    @classmethod
    def get_productopt_bydate(cls, product_ids, date, center_ids=None):

        productopt_obj = ProductOpt.objects \
            .filter(product_id__in=product_ids
                    ) \
            .exclude(Q(start__gt=date) |
                     Q(end__lt=date)
                     )

        if center_ids:
            productopt_obj = productopt_obj.filter(center_id__in=center_ids)

        productopt_records = pd.DataFrame.from_records(productopt_obj.values('center_id',
                                                                             'product_id',
                                                                             'opt',
                                                                             'start',
                                                                             'end',
                                                                             'action_time'
                                                                             ))

        if productopt_records.empty:
            return pd.DataFrame()

        productopt_records = productopt_records \
            .sort_values(['center_id', 'product_id', 'action_time'], ascending=[True, True, True]) \
            .drop_duplicates(['center_id', 'product_id'], keep='last')

        productopt_records['date'] = date

        # if not center_ids:
        #     center_ids = Centers.objects.filter(status='open').values_list('center_id', flat=True)
        # result_list = [
        #     {'center_id': center_id, 'product_id': product_id}
        #     for center_id in center_ids
        #     for product_id in product_ids
        # ]
        #
        # result_records = pd.DataFrame(result_list)
        # result_records = result_records.join(productopt_records.set_index(['center_id', 'product_id']),
        #                                      on=['center_id', 'product_id'], how='left')
        #
        # # result_records.loc[result_records['product_id'].isin(ProductChoice.products_always_opt_in), 'opt'] = 'In'
        # result_records = result_records.where((pd.notna(result_records)), None)

        return productopt_records


class DataDAO:

    @classmethod
    def get_centers(cls, pagination=False, page_size=None, offset=None, filters=None, sort=None, order=None,
                    last_price=False, last_price_product_ids=None, last_price_from_change=True,
                    lastPriceSplit=False, columns=None,
                    as_of_date=None, opt=True):

        if sort and order:
            if order == 'desc':
                sort = '-'+sort
        else:
            sort = 'center_id'

        centers = Centers.objects\
            .filter(status='open') \
            .extra(select={'center_id': 'CAST(center_id AS INTEGER)'})\
            .order_by(sort)

        productopt_records = pd.DataFrame()

        if filters:
            filters = ast.literal_eval(filters)
            #add new column here
            for key, value in filters.items():
                filters_list = value.split(',')
                filters_list = [x.strip() for x in filters_list]
                filters[key] = filters_list
            if filters.get('center_id'):
                filter_item = filters.get('center_id')
                if len(filter_item) == 1:
                    centers = centers.filter(center_id__icontains=filter_item[0])
                else:
                    centers = centers.filter(center_id__in=filter_item)
            if filters.get('center_name'):
                filter_item = filters.get('center_name')
                if len(filter_item) == 1:
                    centers = centers.filter(center_name__icontains=filter_item[0])
                else:
                    centers = centers.filter(reduce(operator.or_, (Q(center_name__icontains=item)
                                                                   for item in filter_item if item)))
            if filters.get('brand'):
                filter_item = filters.get('brand')
                if len(filter_item) == 1:
                    centers = centers.filter(brand__icontains=filter_item[0])
                else:
                    centers = centers.filter(reduce(operator.or_, (Q(brand__icontains=item)
                                                                   for item in filter_item if item)))
            if filters.get('region'):
                filter_item = filters.get('region')
                if len(filter_item) == 1:
                    centers = centers.filter(region__icontains=filter_item[0])
                else:
                    centers = centers.filter(reduce(operator.or_, (Q(region__icontains=item)
                                                                   for item in filter_item if item)))
            if filters.get('district'):
                filter_item = filters.get('district')
                if len(filter_item) == 1:
                    centers = centers.filter(district__icontains=filter_item[0])
                else:
                    centers = centers.filter(reduce(operator.or_, (Q(district__icontains=item)
                                                                   for item in filter_item if item)))
            if filters.get('status'):
                filter_item = filters.get('status')
                if len(filter_item) == 1:
                    centers = centers.filter(status__exact=filter_item[0])
                else:
                    centers = centers.filter(status__in=filter_item)
            if filters.get('sale_region'):
                filter_item = filters.get('sale_region')
                if len(filter_item) == 1:
                    centers = centers.filter(sale_region__icontains=filter_item[0])
                else:
                    centers = centers.filter(reduce(operator.or_, (Q(sale_region__icontains=item)
                                                                   for item in filter_item if item)))
            if filters.get('territory'):
                filter_item = filters.get('territory')
                if len(filter_item) == 1:
                    centers = centers.filter(territory__icontains=filter_item[0])
                else:
                    centers = centers.filter(reduce(operator.or_, (Q(territory__icontains=item)
                                                                   for item in filter_item if item)))
            if filters.get('rvp'):
                filter_item = filters.get('rvp')
                if len(filter_item) == 1:
                    centers = centers.filter(rvp__icontains=filter_item[0])
                else:
                    centers = centers.filter(reduce(operator.or_, (Q(rvp__icontains=item)
                                                                   for item in filter_item if item)))
            if filters.get('time_zone'):
                filter_item = filters.get('time_zone')
                if len(filter_item) == 1:
                    centers = centers.filter(time_zone__icontains=filter_item[0])
                else:
                    centers = centers.filter(reduce(operator.or_, (Q(time_zone__icontains=item)
                                                                   for item in filter_item if item)))
            if filters.get('address'):
                filter_item = filters.get('address')
                if len(filter_item) == 1:
                    centers = centers.filter(address__icontains=filter_item[0])
                else:
                    centers = centers.filter(reduce(operator.or_, (Q(address__icontains=item)
                                                                   for item in filter_item if item)))
            if filters.get('city'):
                filter_item = filters.get('city')
                if len(filter_item) == 1:
                    centers = centers.filter(city__icontains=filter_item[0])
                else:
                    centers = centers.filter(reduce(operator.or_, (Q(city__icontains=item)
                                                                   for item in filter_item if item)))
            if filters.get('state'):
                filter_item = filters.get('state')
                if len(filter_item) == 1:
                    centers = centers.filter(state__icontains=filter_item[0])
                else:
                    centers = centers.filter(reduce(operator.or_, (Q(state__icontains=item)
                                                                   for item in filter_item if item)))
            if filters.get('zipcode'):
                filter_item = filters.get('zipcode')
                if len(filter_item) == 1:
                    centers = centers.filter(zipcode__icontains=filter_item[0])
                else:
                    centers = centers.filter(reduce(operator.or_, (Q(zipcode__icontains=item)
                                                                   for item in filter_item if item)))
            if filters.get('bowling_tier'):
                filter_item = filters.get('bowling_tier')
                if len(filter_item) == 1:
                    centers = centers.filter(bowling_tier__exact=filter_item[0])
                else:
                    centers = centers.filter(bowling_tier__in=filter_item)
            if filters.get('alcohol_tier'):
                filter_item = filters.get('alcohol_tier')
                if len(filter_item) == 1:
                    centers = centers.filter(alcohol_tier__exact=filter_item[0])
                else:
                    centers = centers.filter(alcohol_tier__in=filter_item)
            if filters.get('food_tier'):
                filter_item = filters.get('food_tier')
                if len(filter_item) == 1:
                    centers = centers.filter(food_tier__exact=filter_item[0])
                else:
                    centers = centers.filter(food_tier__in=filter_item)
            if filters.get('food_menu'):
                filter_item = filters.get('food_menu')
                if len(filter_item) == 1:
                    centers = centers.filter(food_menu__icontains=filter_item[0])
                else:
                    centers = centers.filter(reduce(operator.or_, (Q(food_menu__icontains=item)
                                                                   for item in filter_item if item)))
            # if filters.get('weekday_prime'):
            #     filter_item = filters.get('weekday_prime')
            #     if len(filter_item) == 1:
            #         centers = centers.filter(weekday_prime__exact=filter_item[0])
            #     else:
            #         centers = centers.filter(weekday_prime__in=filter_item)
            # if filters.get('weekend_premium'):
            #     filter_item = filters.get('weekend_premium')
            #     if len(filter_item) == 1:
            #         centers = centers.filter(weekend_premium__icontains=filter_item[0])
            #     else:
            #         centers = centers.filter(weekend_premium__in=filter_item)
            if filters.get('center_type'):
                filter_item = filters.get('center_type')
                if len(filter_item) == 1:
                    centers = centers.filter(center_type__icontains=filter_item[0])
                else:
                    centers = centers.filter(reduce(operator.or_, (Q(center_type__icontains=item)
                                                                   for item in filter_item if item)))
            if filters.get('lane'):
                filter_item = filters.get('lane')
                if len(filter_item) == 1:
                    centers = centers.filter(center_type__icontains=filter_item[0])
                else:
                    centers = centers.filter(reduce(operator.or_, (Q(center_type__icontains=item)
                                                                   for item in filter_item if item)))

            # filter by product opt in/out
            if last_price_product_ids and set(filters.keys()) & set(last_price_product_ids):
                centers_opt = []
                for last_price_product_id in last_price_product_ids:
                    filter_item_opt = filters.get(last_price_product_id)
                    if filter_item_opt:
                        if productopt_records.empty:
                            productopt_records = ProductOptGet.get_productopt_bydate(last_price_product_ids, as_of_date)
                        productopt_records_opt = productopt_records[
                            (
                                (productopt_records['product_id'] == last_price_product_id) &
                                (productopt_records['opt'].str.contains(filter_item_opt[0], case=False))
                            )
                        ]
                        productopt_records_opt_CenterId = productopt_records_opt['center_id'].unique().tolist()
                        if centers_opt:
                            centers_opt = list(set(centers_opt) & set(productopt_records_opt_CenterId))
                        else:
                            centers_opt = productopt_records_opt_CenterId
                # if centers_opt:
                centers_opt = list(set(centers_opt))
                centers = centers.filter(center_id__in=centers_opt)

        num = centers.count()

        if pagination:
            paginator = Paginator(centers, page_size,)
            current_page = int(offset/page_size) + 1
            centers = paginator.page(current_page).object_list

        centers_id_list = centers.values_list('center_id', flat=True)
        # add new column here
        centers_record = pd.DataFrame.from_records(centers
                                                   .values('center_id',
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
                                                           'center_type',
                                                           'lane',
                                                           ))

        if centers_record.empty:
            return pd.DataFrame(), 0

        # add last price
        if last_price:
            to_records_list = [
                {'center_id': center_id, 'product_id': product_id}
                for center_id in centers_id_list
                for product_id in last_price_product_ids
            ]
            to_records = pd.DataFrame(to_records_list)

            if last_price_from_change:
                last_price_records = PriceChange.get_last_price(last_price_product_ids, center_ids=centers_id_list,
                                                                as_of_date=as_of_date)
                if not last_price_records.empty:
                    last_price_records.drop(['action_time'], axis=1, inplace=True)
            else:
                last_price_records = DataDAO.LastPrice.get_last_price(last_price_product_ids,
                                                                      center_ids=centers_id_list,
                                                                      as_of_date=as_of_date)

            if not last_price_records.empty:
                last_price_records['center_id'] = last_price_records['center_id'].apply(int)

                to_records = to_records.join(last_price_records.set_index(['center_id', 'product_id']),
                                             on=['center_id', 'product_id'], how='left')
            else:
                to_records['price'] = None

            # add product opt
            if opt:
                if productopt_records.empty:
                    productopt_records = ProductOptGet.get_productopt_bydate(last_price_product_ids, as_of_date)
                if not productopt_records.empty:
                    productopt_records['center_id'] = productopt_records['center_id'].apply(int)
                    productopt_records.drop(['action_time'], axis=1, inplace=True)
                    to_records = to_records.join(productopt_records.set_index(['center_id', 'product_id']),
                                                 on=['center_id', 'product_id'], how='left')
                else:
                    to_records['opt'] = None

                to_records = to_records.where((pd.notnull(to_records)), '')

                # Combine Price and Opt into one new Column
                to_records['PriceOpt'] = to_records[['price', 'opt']] \
                    .apply(lambda x: '${price} / {opt}'.format(price=x['price'], opt=x['opt']),
                           axis=1
                           )
            else:
                to_records['price'] = to_records['price'] \
                    .apply(lambda x: '${price}'.format(price=x))

            product_map = {}
            if not lastPriceSplit:
                to_records = pd.pivot_table(to_records,
                                            index=['center_id'],
                                            columns=['product_id'],
                                            values=['PriceOpt'],
                                            aggfunc='first'
                                            )
            else:
                productValues = Product.objects.filter(product_id__in=last_price_product_ids)\
                    .values('product_id', 'product_name')
                product_map = {productValue['product_id']: productValue['product_name']
                               for productValue in productValues}
                product_map['center_id'] = 'center_id'
                to_records = pd.pivot_table(to_records,
                                            index=['center_id'],
                                            columns=['product_id'],
                                            values=['PriceOpt', 'price', 'opt'],
                                            aggfunc='first'
                                            )
                to_records = to_records[['PriceOpt', 'price', 'opt']]

                # Reorder Product
                ordered_columns = pd.MultiIndex.from_tuples([(attr, id) for attr in ['PriceOpt', 'price', 'opt']
                                                             for id in last_price_product_ids],
                                                            names=[None, 'product_id']
                                                            )
                to_records = to_records.reindex(columns=ordered_columns)

            to_records.columns = to_records.columns.droplevel(0)
            to_records.columns.name = None
            to_records.reset_index(inplace=True)

            # Rename Column name (Product id to Product Name)
            if lastPriceSplit:
                to_records.columns = to_records.columns.to_series().map(product_map)
                centers_record['center_id_'] = centers_record['center_id']

            # Select out the columns and reordered
            if columns:
                centers_record = centers_record[['center_id', 'center_id_'] + columns]

            centers_record = centers_record.join(to_records.set_index('center_id'),
                                                 on='center_id', how='left')

        # add star for session center
        def session_center_star(row):
            if row['center_type'] == 'session':
                return '*{center_id}'.format(center_id=row['center_id'])
            else:
                return row['center_id']
        centers_record['center_id'] = centers_record.apply(session_center_star, axis=1)

        # capitalize string
        centers_record['center_type'] = centers_record['center_type'].str.capitalize()

        return centers_record, num

    # @classmethod
    # def get_centers_extend(cls, pagination=False, page_size=None, offset=None, filters=None, sort=None, order=None):
    #
    #     if sort and order:
    #         if order == 'desc':
    #             sort = '-'+sort
    #     else:
    #         sort = 'center_id'
    #
    #     centers = Centers.objects\
    #         .all() \
    #         .extra(select={'center_id': 'CAST(center_id AS INTEGER)'})\
    #         .order_by(sort)
    #
    #     if filters:
    #         filters = ast.literal_eval(filters)
    #
    #         if filters.get('center_id'):
    #             centers = centers.filter(center_id__contains=filters['center_id'])
    #         if filters.get('center_name'):
    #             centers = centers.filter(center_name__contains=filters['center_name'])
    #         if filters.get('brand'):
    #             centers = centers.filter(brand__contains=filters['brand'])
    #         if filters.get('region'):
    #             centers = centers.filter(region__contains=filters['region'])
    #         if filters.get('district'):
    #             centers = centers.filter(district__contains=filters['district'])
    #         if filters.get('status'):
    #             centers = centers.filter(status__exact=filters['status'])
    #         if filters.get('time_zone'):
    #             centers = centers.filter(time_zone__exact=filters['time_zone'])
    #         if filters.get('address'):
    #             centers = centers.filter(time_zone__exact=filters['address'])
    #         if filters.get('city'):
    #             centers = centers.filter(time_zone__exact=filters['city'])
    #         if filters.get('state'):
    #             centers = centers.filter(time_zone__exact=filters['state'])
    #         if filters.get('zipcode'):
    #             centers = centers.filter(time_zone__exact=filters['zipcode'])
    #         if filters.get('tier'):
    #             centers = centers.filter(tier__exact=filters['tier'])
    #         if filters.get('weekday_prime'):
    #             centers = centers.filter(weekday_prime__exact=filters['weekday_prime'])
    #         if filters.get('weekend_premium'):
    #             centers = centers.filter(weekend_premium__exact=filters['weekend_premium'])
    #
    #     num = centers.count()
    #
    #     if pagination:
    #         paginator = Paginator(centers, page_size,)
    #         current_page = int(offset/page_size) + 1
    #         centers = paginator.page(current_page).object_list
    #
    #     centers_record = pd.DataFrame.from_records(centers
    #                                                .values('center_id',
    #                                                        'center_name',
    #                                                        'brand',
    #                                                        'region',
    #                                                        'district',
    #                                                        'status',
    #                                                        'time_zone',
    #                                                        'address',
    #                                                        'city',
    #                                                        'state',
    #                                                        'zipcode',
    #                                                        'tier',
    #                                                        'weekday_prime',
    #                                                        'weekend_premium',
    #                                                        'openhours__DOW',
    #                                                        'openhours__open_hour',
    #                                                        'openhours__end_hour',
    #                                                        ))
    #
    #     centers_record.rename({'openhours__DOW': 'DOW'}, axis=1, inplace=True)
    #     centers_record.rename({'openhours__open_hour': 'open_hour'}, axis=1, inplace=True)
    #     centers_record.rename({'openhours__end_hour': 'end_hour'}, axis=1, inplace=True)
    #
    #     centers_record['open_hour'] = centers_record['open_hour'].apply(lambda x: str(x))
    #     centers_record['end_hour'] = centers_record['end_hour'].apply(lambda x: str(x))
    #     centers_record['time'] = centers_record[['open_hour', 'end_hour']].apply(lambda x: '-'.join(x), axis=1)
    #     centers_record.drop('open_hour', axis=1, inplace=True)
    #     centers_record.drop('end_hour', axis=1, inplace=True)
    #
    #     # centers_record = pd.pivot_table(centers_record, index=[
    #     #                                                 'address',
    #     #                                                 'brand',
    #     #                                                 'center_id',
    #     #                                                 'center_name',
    #     #                                                 'city',
    #     #                                                 'district',
    #     #                                                 'region',
    #     #                                                 'state',
    #     #                                                 'status',
    #     #                                                 'time_zone',
    #     #                                                 # 'zipcode',
    #     #                                             ],
    #     #                                       columns='DOW',
    #     #                                       values='time').reset_index()
    #
    #
    #     # print(centers_record)
    #
    #     if centers_record.empty:
    #         return pd.DataFrame(), 0
    #
    #     return centers_record, num

    @classmethod
    def get_open_hours(cls, pagination=False, page_size=None, offset=None, filters=None, sort=None, order=None):

        if sort and order:
            if order == 'desc':
                sort = '-'+sort
        else:
            sort = 'center_id'

        centers = Centers.objects\
            .filter(status='open') \
            .extra(select={'center_id': 'CAST(center_id AS INTEGER)'})\
            .order_by(sort)

        if filters:
            filters = ast.literal_eval(filters)

            for key, value in filters.items():
                filters_list = value.split(',')
                filters_list = [x.strip() for x in filters_list]
                filters[key] = filters_list
            if filters.get('center_id'):
                filter_item = filters.get('center_id')
                if len(filter_item) == 1:
                    centers = centers.filter(center_id__icontains=filter_item[0])
                else:
                    centers = centers.filter(center_id__in=filter_item)
            if filters.get('center_name'):
                filter_item = filters.get('center_name')
                if len(filter_item) == 1:
                    centers = centers.filter(center_name__icontains=filter_item[0])
                else:
                    centers = centers.filter(reduce(operator.or_, (Q(center_name__icontains=item)
                                                                   for item in filter_item if item)))

        num = centers.count()

        if pagination:
            paginator = Paginator(centers, page_size,)
            current_page = int(offset/page_size) + 1
            centers = paginator.page(current_page).object_list

        center_list = centers.values_list('center_id', flat=True)

        open_hours_obj = OpenHours.objects.filter(center_id__in=center_list)

        open_hours_record = pd.DataFrame.from_records(open_hours_obj.values(
            'center_id',
            'center_id__center_name',
            'DOW',
            'open_hour',
            'end_hour'
            ))

        open_hours_record.rename({'center_id__center_name': 'center_name'}, axis=1, inplace=True)
        open_hours_record['hours'] = open_hours_record[['open_hour', 'end_hour']] \
            .apply(lambda x: x['open_hour'].strftime("%H:%M:%S") + '-' + x['end_hour'].strftime("%H:%M:%S")
                   if x['open_hour'] and x['end_hour'] else '-'
                   , axis=1)

        open_hours_record = pd.pivot_table(open_hours_record,
                                           index=['center_id', 'center_name'],
                                           columns=['DOW'],
                                           values=['hours'],
                                           aggfunc='first'
                                           )
        open_hours_record.columns = open_hours_record.columns.droplevel(0)
        open_hours_record.columns.name = None
        open_hours_record.reset_index(inplace=True)

        if open_hours_record.empty:
            return pd.DataFrame(), 0

        return open_hours_record, num

    @classmethod
    def get_price_table_v1(cls, start, end,
                           pagination=False, page_size=None, offset=None, filters=None, sort=None, order=None):

        date_range = UDatetime.date_range(start, end)

        # find centers
        if sort and order:
            if order == 'desc':
                sort = '-'+sort
        else:
            sort = 'center_id'

        centers = Centers.objects\
            .all() \
            .order_by(sort)
            # .extra(select={'center_id': 'CAST(center_id AS INTEGER)'})

        if filters:
            filters = ast.literal_eval(filters)

            if filters.get('center_id'):
                centers = centers.filter(center_id=filters['center_id'])
            if filters.get('center_name'):
                centers = centers.filter(center_name__contains=filters['center_name'])
            if filters.get('brand'):
                centers = centers.filter(brand__contains=filters['brand'])
            if filters.get('region'):
                centers = centers.filter(region__contains=filters['region'])
            if filters.get('district'):
                centers = centers.filter(district__contains=filters['district'])
            if filters.get('status'):
                centers = centers.filter(status__exact=filters['status'])
            if filters.get('time_zone'):
                    centers = centers.filter(time_zone__exact=filters['time_zone'])

        num = centers.count()

        if pagination:
            paginator = Paginator(centers, page_size,)
            current_page = int(offset/page_size) + 1
            centers = paginator.page(current_page).object_list

        centers_id_list = centers.values_list('center_id', flat=True)
        centers_name_list = centers.values_list('center_name', flat=True)
        district_list = centers.values_list('district', flat=True)
        region_list = centers.values_list('region', flat=True)
        brand_list = centers.values_list('brand', flat=True)
        bowling_tier_list = centers.values_list('bowling_tier', flat=True)
        food_menu_list = centers.values_list('food_menu', flat=True)

        bowling_price = Centers.objects\
            .filter(
                    Q(center_id__in=centers_id_list) &
                    Q(retailbowlingprice__status='active') &
                    Q(retailbowlingprice__effective_datetime__lte=end) &
                    Q(retailbowlingprice__product_name='retail bowling')
            ) \
            .values(
                'center_id',
                'center_name',
                'district',
                'region',
                'brand',
                'retailbowlingprice__price',
                'retailbowlingprice__effective_datetime',
                'retailbowlingprice__period_label',
                'retailbowlingprice__DOW',
            ) \
            .order_by(
                'center_id',
                '-retailbowlingprice__effective_datetime'
            )

        bowling_price_records = pd.DataFrame.from_records(bowling_price)
        bowling_price_records.rename({'retailbowlingprice__price': 'price'}, axis=1, inplace=True)
        bowling_price_records.rename({'retailbowlingprice__effective_datetime': 'effective_datetime'},
                                     axis=1, inplace=True)
        bowling_price_records.rename({'retailbowlingprice__period_label': 'period_label'}, axis=1, inplace=True)
        bowling_price_records.rename({'retailbowlingprice__DOW': 'DOW'}, axis=1, inplace=True)

        shoe_price = Centers.objects\
            .filter(
                    Q(center_id__in=centers_id_list) &
                    Q(retailshoeprice__status='active') &
                    Q(retailshoeprice__effective_datetime__lte=end) &
                    Q(retailshoeprice__product_name='retail shoes')
                   )\
            .values(
                'center_id',
                'center_name',
                'district',
                'region',
                'brand',
                'retailshoeprice__price',
                'retailshoeprice__effective_datetime',
                'retailshoeprice__period_label',
                'retailshoeprice__DOW',
            ) \
            .order_by(
                'center_id',
                '-retailshoeprice__effective_datetime'
            )

        shoe_price_records = pd.DataFrame.from_records(shoe_price)
        shoe_price_records.rename({'retailshoeprice__price': 'price'}, axis=1, inplace=True)
        shoe_price_records.rename({'retailshoeprice__effective_datetime': 'effective_datetime'}, axis=1, inplace=True)
        shoe_price_records.rename({'retailshoeprice__period_label': 'period_label'}, axis=1, inplace=True)
        shoe_price_records.rename({'retailshoeprice__DOW': 'DOW'}, axis=1, inplace=True)

        food_price = Centers.objects\
            .filter(center_id__in=centers_id_list,
                    ) \
            .annotate(
                food_price=Avg('retailfoodprice__price',
                               filter=Q(retailfoodprice__status='active')
                 )
            ) \
            .values(
                'center_id',
                'center_name',
                'food_price',
                'food_menu',
                'food_tier'
            )\

        food_price_records = pd.DataFrame.from_records(food_price)

        food_price_records['food_price'] = food_price_records['food_price'].apply(lambda x:round(float(x), 2))

        columns = ['center_id', 'center_name', 'district', 'region', 'brand', 'bowling_tier', 'product', 'food_menu']
        for date in date_range:
            columns += ['{date}-nonprime'.format(date=date.strftime('%Y%m%d'))]
            columns += ['{date}-prime'.format(date=date.strftime('%Y%m%d'))]
            columns += ['{date}-premium'.format(date=date.strftime('%Y%m%d'))]
        result_record = pd.DataFrame(columns=columns)

        centers_id_list_repeat = list(itertools.chain.from_iterable(itertools.repeat(x, 3) for x in centers_id_list))
        centers_name_list_repeat = list(itertools.chain.from_iterable(itertools.repeat(x, 3)
                                                                      for x in centers_name_list))
        product_list_repeat = ['bowling', 'shoe', 'food'] * len(centers_id_list)
        district_list_repeat = list(itertools.chain.from_iterable(itertools.repeat(x, 3) for x in district_list))
        region_list_repeat = list(itertools.chain.from_iterable(itertools.repeat(x, 3) for x in region_list))
        brand_list_repeat = list(itertools.chain.from_iterable(itertools.repeat(x, 3) for x in brand_list))
        bowling_tier_list_repeat = list(itertools.chain.from_iterable(itertools.repeat(x, 3)
                                                                      for x in bowling_tier_list))
        food_menu_list_repeat = list(itertools.chain.from_iterable(itertools.repeat(x, 3) for x in food_menu_list))
        for idx, val in enumerate(food_menu_list_repeat):
            if (idx + 1) % 3 != 0:
                food_menu_list_repeat[idx] = ''

        result_record['center_id'] = centers_id_list_repeat
        result_record['center_name'] = centers_name_list_repeat
        result_record['product'] = product_list_repeat
        result_record['district'] = district_list_repeat
        result_record['region'] = region_list_repeat
        result_record['brand'] = brand_list_repeat
        result_record['bowling_tier'] = bowling_tier_list_repeat
        result_record['food_menu'] = food_menu_list_repeat

        for index, row in result_record.iterrows():
            for date in date_range:
                if row['product'] == 'bowling':
                    records = bowling_price_records
                elif row['product'] == 'shoe':
                    records = shoe_price_records
                else:
                    records = pd.DataFrame()

                if not records.empty:
                    dow = DOW_choice[date.weekday()][0]

                    nonprime_price = records[
                        (records['center_id'] == row['center_id']) &
                        (records['period_label'] == 'non-prime') &
                        (records['effective_datetime'] <= date) &
                        (records['DOW'] == dow)
                    ]

                    if not nonprime_price.empty:
                        result_record.at[index, '{date}-nonprime'.format(date=date.strftime('%Y%m%d'))] = \
                                                nonprime_price['price'].values[0]

                    prime_price = records[
                        (records['center_id'] == row['center_id']) &
                        (records['period_label'] == 'prime') &
                        (records['effective_datetime'] <= date) &
                        (records['DOW'] == dow)
                    ]
                    if not prime_price.empty:
                        result_record.at[index, '{date}-prime'.format(date=date.strftime('%Y%m%d'))] = \
                                                prime_price['price'].values[0]

                    premium_price = records[
                        (records['center_id'] == row['center_id']) &
                        (records['period_label'] == 'premium') &
                        (records['effective_datetime'] <= date) &
                        (records['DOW'] == dow)
                    ]
                    if not premium_price.empty:
                        result_record.at[index, '{date}-premium'.format(date=date.strftime('%Y%m%d'))] = \
                            premium_price['price'].values[0]

            if row['product'] == 'food':
                records = food_price_records
            else:
                records = pd.DataFrame()

            if not records.empty:
                date = date_range[0]
                food_price = records[
                    (records['center_id'] == row['center_id'])
                ]

                if not food_price.empty:
                    result_record.at[index, '{date}-nonprime'.format(date=date.strftime('%Y%m%d'))] = \
                        food_price['food_price'].values[0]

                result_record.at[index, 'bowling_tier'] = food_price['food_tier'].values[0]

        result_record['product'] = result_record['product'].apply(lambda x: x.capitalize())

        return result_record, num
        # return pd.DataFrame, 0

    @classmethod
    def get_price_table_v2(cls, start, end, product,
                           pagination=False, page_size=None, offset=None, filters=None, sort=None, order=None):

        # init
        date_range = UDatetime.date_range(start, end)
        retail_bowling_non_prime_product_ids = ['101', '104']
        retail_bowling_prime_product_ids = ['102', '105']
        retail_bowling_premium_product_ids = ['103', '106']
        retail_shoe_product_ids = ['107']

        product_len = len(product)

        if 'retail bowling' in product:
            RETAIL_BOWLING = True
        else:
            RETAIL_BOWLING = False
        if 'retail shoe' in product:
            RETAIL_SHOE = True
        else:
            RETAIL_SHOE = False
        if 'retail food' in product:
            RETAIL_FOOD = True
        else:
            RETAIL_FOOD = False

        # find centers
        if sort and order:
            if order == 'desc':
                sort = '-'+sort
        else:
            sort = 'center_id'

        centers = Centers.objects\
            .all() \
            .order_by(sort) \
            .extra(select={'center_id': 'CAST(center_id AS INTEGER)'})

        if filters:
            filters = ast.literal_eval(filters)

            if filters.get('center_id'):
                centers = centers.filter(center_id=filters['center_id'])
            if filters.get('center_name'):
                centers = centers.filter(center_name__contains=filters['center_name'])
            if filters.get('brand'):
                centers = centers.filter(brand__contains=filters['brand'])
            if filters.get('region'):
                centers = centers.filter(region__contains=filters['region'])
            if filters.get('district'):
                centers = centers.filter(district__contains=filters['district'])
            if filters.get('status'):
                centers = centers.filter(status__exact=filters['status'])
            if filters.get('time_zone'):
                    centers = centers.filter(time_zone__exact=filters['time_zone'])

        num = centers.count()

        if pagination:
            paginator = Paginator(centers, page_size,)
            current_page = int(offset/page_size) + 1
            centers = paginator.page(current_page).object_list

        centers_id_list = centers.values_list('center_id', flat=True)
        centers_name_list = centers.values_list('center_name', flat=True)
        district_list = centers.values_list('district', flat=True)
        region_list = centers.values_list('region', flat=True)
        brand_list = centers.values_list('brand', flat=True)
        bowling_tier_list = centers.values_list('bowling_tier', flat=True)
        food_menu_list = centers.values_list('food_menu', flat=True)
        centers_id_list = [str(x) for x in centers_id_list]

        if RETAIL_BOWLING:
            bowling_price = Centers.objects\
                .filter(
                        Q(center_id__in=centers_id_list) &
                        Q(retailbowlingprice__date__range=[start, end])
                ) \
                .values(
                    'center_id',
                    'center_name',
                    'district',
                    'region',
                    'brand',
                    'retailbowlingprice__price',
                    'retailbowlingprice__date',
                    'retailbowlingprice__product_id',
                    'retailbowlingprice__DOW'
                ) \
                .order_by(
                    'center_id',
                    '-retailbowlingprice__date'
                )

            bowling_price_records = pd.DataFrame.from_records(bowling_price)
            bowling_price_records.rename({'retailbowlingprice__price': 'price',
                                          'retailbowlingprice__date': 'date',
                                          'retailbowlingprice__product_id': 'product_id',
                                          'retailbowlingprice__DOW': 'DOW'
                                          },
                                         axis=1, inplace=True
                                         )

        if RETAIL_SHOE:
            shoe_price = Centers.objects\
                .filter(
                        Q(center_id__in=centers_id_list) &
                        Q(retailshoeprice__date__range=[start, end])
                ) \
                .values(
                    'center_id',
                    'center_name',
                    'district',
                    'region',
                    'brand',
                    'retailshoeprice__price',
                    'retailshoeprice__date',
                    'retailshoeprice__product_id',
                    'retailshoeprice__DOW'
                ) \
                .order_by(
                    'center_id',
                    '-retailshoeprice__date'
                )

            shoe_price_records = pd.DataFrame.from_records(shoe_price)
            shoe_price_records.rename({'retailshoeprice__price': 'price',
                                       'retailshoeprice__date': 'date',
                                       'retailshoeprice__product_id': 'product_id',
                                       'retailshoeprice__DOW': 'DOW'
                                       },
                                       axis=1, inplace=True
                                      )

        if RETAIL_FOOD:
            food_price = Centers.objects\
                .filter(center_id__in=centers_id_list,
                        ) \
                .annotate(
                    food_price=Avg('retailfoodprice__price',
                                   filter=Q(retailfoodprice__status='active')
                    )
                ) \
                .values(
                    'center_id',
                    'center_name',
                    'food_price',
                    'food_menu',
                    'food_tier'
                )\

            food_price_records = pd.DataFrame.from_records(food_price)
            food_price_records['food_price'] = food_price_records['food_price'].apply(lambda x:round(float(x), 2))

        # Other products
        product_price = Centers.objects \
            .filter(
                    Q(center_id__in=centers_id_list) &
                    Q(productprice__date__range=[start, end]) &
                    Q(productprice__product_name__in=product)
            ) \
            .values(
                'center_id',
                'center_name',
                'district',
                'region',
                'brand',
                'productprice__price',
                'productprice__date',
                'productprice__product_id',
                'productprice__product_name',
                'productprice__DOW'
            ) \
            .order_by(
                'center_id',
                '-productprice__date'
            )

        if product_price.exists():

            product_price_records = pd.DataFrame.from_records(product_price)
            product_price_records.rename({'productprice__price': 'price',
                                          'productprice__date': 'date',
                                          'productprice__product_id': 'product_id',
                                          'productprice__product_name': 'product_name',
                                          'productprice__DOW': 'DOW'
                                          },
                                         axis=1, inplace=True
                                         )
        else:
            product_price_records = pd.DataFrame()


        # Init Output Dataframe
        columns = ['center_id', 'center_name', 'district', 'region', 'brand', 'shoe_tier', 'product', 'food_menu']
        for date in date_range:
            columns += ['{date}-nonprime'.format(date=date.strftime('%Y%m%d'))]
            columns += ['{date}-prime'.format(date=date.strftime('%Y%m%d'))]
            columns += ['{date}-premium'.format(date=date.strftime('%Y%m%d'))]
        result_record = pd.DataFrame(columns=columns)

        centers_id_list_repeat = list(itertools.chain.from_iterable(itertools.repeat(x, product_len)
                                                                    for x in centers_id_list))
        centers_name_list_repeat = list(itertools.chain.from_iterable(itertools.repeat(x, product_len)
                                                                      for x in centers_name_list))
        product_list_repeat = product * len(centers_id_list)
        district_list_repeat = list(itertools.chain.from_iterable(itertools.repeat(x, product_len)
                                                                  for x in district_list))
        region_list_repeat = list(itertools.chain.from_iterable(itertools.repeat(x, product_len) for x in region_list))
        brand_list_repeat = list(itertools.chain.from_iterable(itertools.repeat(x, product_len) for x in brand_list))
        bowling_tier_list_repeat = list(itertools.chain.from_iterable(itertools.repeat(x, product_len)
                                                                      for x in bowling_tier_list))

        if RETAIL_FOOD:
            food_menu_list_repeat = list(itertools.chain.from_iterable(itertools.repeat(x, product_len)
                                                                       for x in food_menu_list))
            for idx, val in enumerate(food_menu_list_repeat):
                if (idx + 1) % product_len != 0:
                    food_menu_list_repeat[idx] = ''

        result_record['center_id'] = centers_id_list_repeat
        result_record['center_name'] = centers_name_list_repeat
        result_record['product'] = product_list_repeat
        result_record['district'] = district_list_repeat
        result_record['region'] = region_list_repeat
        result_record['brand'] = brand_list_repeat
        result_record['bowling_tier'] = bowling_tier_list_repeat
        if RETAIL_FOOD:
            result_record['food_menu'] = food_menu_list_repeat

        for index, row in result_record.iterrows():
            for date in date_range:
                dow = DOW_choice[date.weekday()][0]
                if row['product'] == 'retail bowling':
                    records = bowling_price_records
                    if not records.empty:
                        nonprime_price = records[
                            (records['center_id'] == row['center_id']) &
                            (records['date'] == date.date()) &
                            (records['DOW'] == dow) &
                            (records['product_id'].isin(retail_bowling_non_prime_product_ids))
                        ]

                        if not nonprime_price.empty:
                            result_record.at[index, '{date}-nonprime'.format(date=date.strftime('%Y%m%d'))] = \
                                                    nonprime_price['price'].values[0]

                        prime_price = records[
                            (records['center_id'] == row['center_id']) &
                            (records['date'] == date.date()) &
                            (records['DOW'] == dow) &
                            (records['product_id'].isin(retail_bowling_prime_product_ids))
                        ]
                        if not prime_price.empty:
                            result_record.at[index, '{date}-prime'.format(date=date.strftime('%Y%m%d'))] = \
                                                    prime_price['price'].values[0]

                        premium_price = records[
                            (records['center_id'] == row['center_id']) &
                            (records['date'] == date.date()) &
                            (records['DOW'] == dow) &
                            (records['product_id'].isin(retail_bowling_premium_product_ids))
                        ]
                        if not premium_price.empty:
                            result_record.at[index, '{date}-premium'.format(date=date.strftime('%Y%m%d'))] = \
                                premium_price['price'].values[0]
                elif row['product'] == 'retail shoe':
                    records = shoe_price_records
                    if not records.empty:
                        nonprime_price = records[
                            (records['center_id'] == row['center_id']) &
                            (records['date'] == date.date()) &
                            (records['DOW'] == dow) &
                            (records['product_id'].isin(retail_shoe_product_ids))
                            ]

                        if not nonprime_price.empty:
                            result_record.at[index, '{date}-nonprime'.format(date=date.strftime('%Y%m%d'))] = \
                                nonprime_price['price'].values[0]
                elif row['product'] in ['Sunday Funday Bowling',
                                        'Sunday Funday Shoes',
                                        'Monday Mayhem AYCB',
                                        '222 Tuesday Game',
                                        'College night'] \
                        and not product_price_records.empty:

                    records = product_price_records
                    if not records.empty:
                        nonprime_price = records[
                            (records['center_id'] == row['center_id']) &
                            (records['date'] == date.date()) &
                            (records['DOW'] == dow) &
                            (records['product_name'] == row['product'])
                            ]

                        if not nonprime_price.empty:
                            result_record.at[index, '{date}-nonprime'.format(date=date.strftime('%Y%m%d'))] = \
                                nonprime_price['price'].values[0]

            if row['product'] == 'retail food':
                records = food_price_records
            else:
                records = pd.DataFrame()

            if not records.empty:
                date = date_range[0]
                food_price = records[
                    (records['center_id'] == row['center_id'])
                ]

                if not food_price.empty:
                    result_record.at[index, '{date}-nonprime'.format(date=date.strftime('%Y%m%d'))] = \
                        food_price['food_price'].values[0]

                result_record.at[index, 'bowling_tier'] = food_price['food_tier'].values[0]

        result_record['product'] = result_record['product'].apply(lambda x: x.capitalize())

        return result_record, num
        # return pd.DataFrame, 0

    @classmethod
    def get_price_table_v3(cls, start, end, product,
                           pagination=False, page_size=None, offset=None, filters=None, sort=None, order=None):

        # init
        date_range = UDatetime.date_range(start, end)
        product_ids = []

        center_name_replace = {
            'AMF': '',
            'Bowlero': '',
            'Bowlmor': '',
            'Brunswick Zone': ''
        }

        result_record = pd.DataFrame()

        retail_bowling_list = Product.objects.filter(report_type='Retail Bowling', status='active')\
            .values_list('product_id', flat=True)
        retail_shoe_list = Product.objects.filter(report_type='Retail Shoe', status='active')\
            .values_list('product_id', flat=True)
        product_list = Product.objects.filter(report_type='Retail Promos', status='active')\
            .values_list('product_id', flat=True)

        if set(product) & set(retail_bowling_list):
            RETAIL_BOWLING = True
            # product.pop('retail bowling', None)
        else:
            RETAIL_BOWLING = False
        if set(product) & set(retail_shoe_list):
            RETAIL_SHOE = True
        else:
            RETAIL_SHOE = False
        if set(product) & set(product_list):
            PRODUCT = True
        else:
            PRODUCT = False

        # find centers
        if sort and order:
            if order == 'desc':
                sort = '-'+sort
        else:
            sort = 'center_id'

        centers = Centers.objects\
            .filter(status='open') \
            .extra(select={'center_id': 'CAST(center_id AS INTEGER)'}) \
            .order_by(sort)

        if filters:
            filters = ast.literal_eval(filters)

            for key, value in filters.items():
                filters[key] = value.split(',')
            if filters.get('center_id'):
                filter_item = filters.get('center_id')
                if len(filter_item) == 1:
                    centers = centers.filter(center_id__icontains=filter_item[0])
                else:
                    centers = centers.filter(center_id__in=filter_item)
            if filters.get('center_name'):
                centers = centers.filter(center_name__contains=filters['center_name'])
            if filters.get('brand'):
                centers = centers.filter(brand__contains=filters['brand'])
            if filters.get('region'):
                centers = centers.filter(region__contains=filters['region'])
            if filters.get('district'):
                centers = centers.filter(district__contains=filters['district'])
            if filters.get('status'):
                centers = centers.filter(status__exact=filters['status'])
            if filters.get('time_zone'):
                centers = centers.filter(time_zone__exact=filters['time_zone'])
            if filters.get('bowling_tier'):
                centers = centers.filter(bowling_tier__contains=filters['bowling_tier'])
            if filters.get('food_tier'):
                centers = centers.filter(food_tier__contains=filters['food_tier'])
            if filters.get('food_menu'):
                centers = centers.filter(food_menu__contains=filters['food_menu'])

        num = centers.count()

        if pagination:
            paginator = Paginator(centers, page_size,)
            current_page = int(offset/page_size) + 1
            centers = paginator.page(current_page).object_list

        centers_id_list = centers.values_list('center_id', flat=True)
        centers_id_list = [str(x) for x in centers_id_list]
        if not centers_id_list:
            return result_record, num

        # get price data
        if RETAIL_BOWLING:
            bowling_price = RetailBowlingPrice.objects\
                .filter(
                        Q(center_id__center_id__in=centers_id_list) &
                        Q(date__range=[start, end]) &
                        Q(product_id__product_id__in=product)
                )

            bowling_price_records = pd.DataFrame.from_records(
                bowling_price.values(
                    'center_id__center_id',
                    'price',
                    'date',
                    'product_id',
                ))
            bowling_price_records.rename({'center_id__center_id': 'center_id',
                                          }, axis=1, inplace=True)
        else:
            bowling_price_records = pd.DataFrame()

        if RETAIL_SHOE:
            shoe_price = RetailShoePrice.objects\
                .filter(
                        Q(center_id__center_id__in=centers_id_list) &
                        Q(date__range=[start, end]) &
                        Q(product_id__product_id__in=product)
                )

            shoe_price_records = pd.DataFrame.from_records(
                shoe_price.values(
                    'center_id__center_id',
                    'price',
                    'date',
                    'product_id',
                ))
            shoe_price_records.rename({'center_id__center_id': 'center_id',
                                       }, axis=1, inplace=True)
        else:
            shoe_price_records = pd.DataFrame()

        # if RETAIL_FOOD:
        #     food_price = Centers.objects\
        #         .filter(center_id__in=centers_id_list,
        #                 ) \
        #         .values(
        #             'center_id',
        #             'center_name',
        #             'district',
        #             'region',
        #             'brand',
        #             'food_tier',
        #             'food_menu'
        #         )
        #
        #     # price_by_menu = FoodMenuTable.objects \
        #     #     .values(
        #     #         'menu',
        #     #         'tier'
        #     #     ) \
        #     #     .annotate(
        #     #             price=Avg('price',
        #     #         )
        #     #     ) \
        #
        #     # price_by_menu_records = pd.DataFrame.from_records(price_by_menu)
        #     # price_by_menu_records['price'] = price_by_menu_records['price'].apply(lambda x: round(float(x), 2))
        #     # price_by_menu_records['tier'].replace({'tier ': ''}, inplace=True, regex=True)
        #     # price_by_menu_records.rename({'menu': 'food_menu'}, axis=1, inplace=True)
        #
        #     food_price_records = pd.DataFrame.from_records(food_price)
        #     food_price_records.rename({
        #                                'food_tier': 'tier'
        #                                },
        #                                axis=1, inplace=True
        #                               )
        #     food_price_records['product'] = 'Retail Food'
        #     food_price_records['date'] = date_range[0].date()
        #
        #     # print(price_by_menu_records)
        #
        #     # food_price_records = pd.merge(food_price_records, price_by_menu_records,
        #     how='left', on=['food_menu', 'tier'])
        #
        #     result_record = pd.concat([result_record, food_price_records], axis=0, ignore_index=True)

        # Other products
        if PRODUCT:
            product_price = ProductPrice.objects \
                .filter(
                    Q(center_id__center_id__in=centers_id_list) &
                    Q(date__range=[start, end]) &
                    Q(product_id__product_id__in=product)
                )

            product_price_records = pd.DataFrame.from_records(
                product_price.values(
                    'center_id__center_id',
                    'price',
                    'date',
                    'product_id',
                ))
            product_price_records.rename({'center_id__center_id': 'center_id',
                                          }, axis=1, inplace=True)
        else:
            product_price_records = pd.DataFrame()

        price_record = pd.concat([bowling_price_records, shoe_price_records, product_price_records],
                                 axis=0, ignore_index=True)

        # concat data
        centers_records = pd.DataFrame.from_records(centers.values('center_id',
                                                                   'center_name',
                                                                   'district',
                                                                   'region',
                                                                   'brand',
                                                                   'bowling_tier',
                                                                   'food_tier',
                                                                   'food_menu',
                                                                   'center_type'
                                                                   ))
        centers_records['center_id'] = centers_records['center_id'].astype('str')

        # init result records
        result_list = [
            {'center_id': center_id,
             'product_id': product_id
             }
            for center_id in centers_id_list for product_id in product
        ]
        result_record = pd.DataFrame(result_list)
        result_record = result_record.join(centers_records.set_index(['center_id']),
                                           on=['center_id'], how='left')
        # result_record = result_record[
        #     ~(
        #         ((result_record['center_type'] == 'traditional') & (result_record['product_id']
        #         .isin(ProductChoice.retail_bowling_experiential_center))) |
        #         ((result_record['center_type'] == 'experiential') & (result_record['product_id']
        #         .isin(ProductChoice.retail_bowling_traditional_center))) |
        #         ((result_record['center_type'] == 'session') & (result_record['product_id']
        #         .isin(ProductChoice.retail_bowling_experiential_center)))
        #     )
        # ]
        # Product
        product_obj = Product.objects.filter(product_id__in=product)
        if product_obj.exists():
            product_records = pd.DataFrame.from_records(product_obj.values('product_id', 'short_product_name'))
            product_records.rename({'short_product_name': 'product_name'}, axis=1, inplace=True)
            result_record = result_record.join(product_records.set_index(['product_id']),
                                               on=['product_id'], how='left')
        else:
            result_record['product_name'] = None

        # Product Opt
        product_opt = ProductOptGet.get_productopt(product, start, end, centers_id_list)
        if not product_opt.empty:
            product_opt_one = product_opt.drop_duplicates(['center_id', 'product_id'])
            result_record = result_record.join(product_opt_one.set_index(['center_id', 'product_id']),
                                               on=['center_id', 'product_id'], how='left')
            if not price_record.empty:
                price_record['date'] = pd.to_datetime(price_record['date'])
                price_record = price_record.join(product_opt.set_index(['center_id', 'product_id', 'date']),
                                                 on=['center_id', 'product_id', 'date'], how='left')
                price_record = price_record[~(price_record['opt'] == 'Out')]
        else:
            result_record['opt'] = None
        # result_record = result_record.where((pd.notnull(result_record)), '')

        # Product Price
        if not price_record.empty:

            # filter out product opt out
            price_record['date'] = price_record['date'].apply(lambda x: str(x.date()))
            price_record['price'] = price_record['price'].apply(lambda x: '${price}'.format(price=x))
            # result_record = result_record.where((pd.notnull(result_record)), "")

            price_record = pd.pivot_table(price_record,
                                          index=['center_id', 'product_id'],
                                          columns=['date'],
                                          values=['price'],
                                          aggfunc='first'
                                         )

            price_record.columns = price_record.columns.droplevel(0)
            price_record.columns.name = None
            price_record.reset_index(inplace=True)

            for date in date_range:
                date = str(date)
                if date not in price_record.columns:
                    price_record[date] = np.nan

            result_record = result_record.join(price_record.set_index(['center_id', 'product_id']),
                                               on=['center_id', 'product_id'], how='left')
        else:
            for date in date_range:
                date = str(date)
                result_record[date] = np.nan

        result_record['center_name'].replace(center_name_replace, inplace=True, regex=True)
        result_record.sort_values(['center_id', 'product_id'], inplace=True)

        return result_record, num

    @classmethod
    def get_price_table(cls, start, end, product, pagination=False, page_size=None, offset=None, filters=None,
                        sort=None, order=None):

        # init
        date_range = UDatetime.date_range(start, end)

        center_name_replace = {
            'AMF': '',
            'Bowlero': '',
            'Bowlmor': '',
            'Brunswick Zone': ''
        }

        result_record = pd.DataFrame()

        # find centers
        if sort and order:
            if order == 'desc':
                sort = '-' + sort
        else:
            sort = 'center_id'

        centers = Centers.objects \
            .filter(status='open') \
            .extra(select={'center_id': 'CAST(center_id AS INTEGER)'}) \
            .order_by(sort)

        if filters:
            filters = ast.literal_eval(filters)
            for key, value in filters.items():
                filters_list = value.split(',')
                filters_list = [x.strip() for x in filters_list]
                filters[key] = filters_list
            if filters.get('center_id'):
                filter_item = filters.get('center_id')
                if len(filter_item) == 1:
                    centers = centers.filter(center_id__icontains=filter_item[0])
                else:
                    centers = centers.filter(center_id__in=filter_item)
            if filters.get('center_name'):
                filter_item = filters.get('center_name')
                if len(filter_item) == 1:
                    centers = centers.filter(center_name__icontains=filter_item[0])
                else:
                    centers = centers.filter(reduce(operator.or_, (Q(center_name__icontains=item)
                                                                   for item in filter_item if item)))
            if filters.get('brand'):
                filter_item = filters.get('brand')
                if len(filter_item) == 1:
                    centers = centers.filter(brand__icontains=filter_item[0])
                else:
                    centers = centers.filter(reduce(operator.or_, (Q(brand__icontains=item)
                                                                   for item in filter_item if item)))
            if filters.get('region'):
                filter_item = filters.get('region')
                if len(filter_item) == 1:
                    centers = centers.filter(region__icontains=filter_item[0])
                else:
                    centers = centers.filter(reduce(operator.or_, (Q(region__icontains=item)
                                                                   for item in filter_item if item)))
            if filters.get('district'):
                filter_item = filters.get('district')
                if len(filter_item) == 1:
                    centers = centers.filter(district__icontains=filter_item[0])
                else:
                    centers = centers.filter(reduce(operator.or_, (Q(district__icontains=item)
                                                                   for item in filter_item if item)))
            if filters.get('status'):
                filter_item = filters.get('status')
                if len(filter_item) == 1:
                    centers = centers.filter(status__exact=filter_item[0])
                else:
                    centers = centers.filter(status__in=filter_item)
            if filters.get('time_zone'):
                filter_item = filters.get('time_zone')
                if len(filter_item) == 1:
                    centers = centers.filter(time_zone__icontains=filter_item[0])
                else:
                    centers = centers.filter(reduce(operator.or_, (Q(time_zone__icontains=item)
                                                                   for item in filter_item if item)))
            if filters.get('bowling_tier'):
                filter_item = filters.get('bowling_tier')
                if len(filter_item) == 1:
                    centers = centers.filter(bowling_tier__exact=filter_item[0])
                else:
                    centers = centers.filter(bowling_tier__in=filter_item)
            if filters.get('food_tier'):
                filter_item = filters.get('food_tier')
                if len(filter_item) == 1:
                    centers = centers.filter(food_tier__exact=filter_item[0])
                else:
                    centers = centers.filter(food_tier__in=filter_item)
            if filters.get('food_menu'):
                filter_item = filters.get('food_menu')
                if len(filter_item) == 1:
                    centers = centers.filter(food_menu__icontains=filter_item[0])
                else:
                    centers = centers.filter(reduce(operator.or_, (Q(food_menu__icontains=item)
                                                                   for item in filter_item if item)))

        num = centers.count()

        if pagination:
            paginator = Paginator(centers, page_size, )
            current_page = int(offset / page_size) + 1
            centers = paginator.page(current_page).object_list

        centers_id_list = centers.values_list('center_id', flat=True)
        centers_id_list = [str(x) for x in centers_id_list]
        if not centers_id_list:
            return result_record, num

        # init result records
        result_list = [
            {'center_id': center_id,
             'product_id': product_id
             }
            for center_id in centers_id_list for product_id in product
        ]
        result_record = pd.DataFrame(result_list)

        # Center
        centers_records = pd.DataFrame.from_records(centers.values('center_id',
                                                                   'center_name',
                                                                   'district',
                                                                   'region',
                                                                   'brand',
                                                                   'bowling_event_tier',
                                                                   'food_tier',
                                                                   'food_menu',
                                                                   'center_type'
                                                                   ))
        centers_records['center_id'] = centers_records['center_id'].astype('str')
        result_record = result_record.join(centers_records.set_index(['center_id']),
                                           on=['center_id'], how='left')

        # Product
        product_obj = Product.objects.filter(product_id__in=product)
        if product_obj.exists():
            product_records = pd.DataFrame.from_records(product_obj.values('product_id', 'short_product_name'))
            product_records.rename({'short_product_name': 'product_name'}, axis=1, inplace=True)
            result_record = result_record.join(product_records.set_index(['product_id']),
                                               on=['product_id'], how='left')
        else:
            result_record['product_name'] = None

        # Product Opt
        product_opt = ProductOptGet.get_productopt(product, start, end, centers_id_list)
        product_opt_one = product_opt.drop_duplicates(['center_id', 'product_id'])
        if not product_opt.empty:
            result_record = result_record.join(product_opt_one.set_index(['center_id', 'product_id']),
                                               on=['center_id', 'product_id'], how='left')
        else:
            result_record['opt'] = None
        result_record = result_record.where((pd.notnull(result_record)), '')

        # Product Price
        price_record = PriceChange.get_price_by_date_range(product, start, end, centers_id_list)
        if not price_record.empty:

            # filter out product opt out
            price_record['date'] = price_record['date'].apply(lambda x: str(x.date()))
            price_record['price'] = price_record['price'].apply(lambda x: '${price}'.format(price=x))
            # result_record = result_record.where((pd.notnull(result_record)), "")

            price_record = pd.pivot_table(price_record,
                                          index=['center_id', 'product_id'],
                                          columns=['date'],
                                          values=['price'],
                                          aggfunc='first'
                                          )

            price_record.columns = price_record.columns.droplevel(0)
            price_record.columns.name = None
            price_record.reset_index(inplace=True)

            for date in date_range:
                date = str(date)
                if date not in price_record.columns:
                    price_record[date] = np.nan

            result_record = result_record.join(price_record.set_index(['center_id', 'product_id']),
                                               on=['center_id', 'product_id'], how='left')
        else:
            for date in date_range:
                date = str(date)
                result_record[date] = np.nan

        result_record['center_name'].replace(center_name_replace, inplace=True, regex=True)
        result_record.sort_values(['center_id', 'product_id'], inplace=True)

        return result_record, num

    @classmethod
    def get_food(cls, date, food_menu,
                 pagination=False, page_size=None, offset=None, filters=None, sort=None, order=None):

        if sort and order:
            if order == 'desc':
                sort = '-'+sort
        else:
            sort = 'category'

        food_objs = FoodMenuTable.objects \
            .filter(menu__name=food_menu,
                    menu__status='active',
                    product__status='active',
                    status='active'
                    ) \
            .order_by(sort)

        if filters:
            filters = ast.literal_eval(filters)

            if filters.get('food'):
                food_objs = food_objs.filter(product__product_name__contains=filters['food'])
            if filters.get('menu'):
                food_objs = food_objs.filter(menu__name=filters['menu'])
            if filters.get('category'):
                food_objs = food_objs.filter(category__contains=filters['category'])
            if filters.get('product_num'):
                food_objs = food_objs.filter(product__product_num__contains=filters['product_num'])

        # num = food_objs.count()

        # if pagination:
        #     paginator = Paginator(food_objs, page_size,)
        #     current_page = int(offset/page_size) + 1
        #     food_menu_master = paginator.page(current_page).object_list
        #

        food_objs_record = pd.DataFrame.from_records(food_objs.values(
            'product__product_id',
            'product__product_name',
            'product__product_num',
            'product__productschedule__start',
            'product__productschedule__end',
            'menu__name',
            'menu__menu_id',
            'category',
            'tier',
            'price'
        ))
        #
        food_objs_record.rename({
                                    'product__product_id': 'product_id',
                                    'product__product_name': 'food',
                                    'product__product_num': 'product_num',
                                    'product__productschedule__start': 'start',
                                    'product__productschedule__end': 'end',
                                    'menu__name': 'menu',
                                    'menu__menu_id': 'menu_id'
                                   }, axis=1, inplace=True)

        if food_objs_record.empty:
            return pd.DataFrame(), 0

        food_objs_record['start'] = food_objs_record['start'].apply(lambda x: x.date() if x else x)
        food_objs_record['end'] = food_objs_record['end'].apply(lambda x: x.date() if x else x)

        food_objs_record_join = food_objs_record[['food', 'product_num', 'start', 'end',
                                                  'product_id', 'menu_id', 'menu', 'category']]
        food_objs_record_join = food_objs_record_join.drop_duplicates(subset=['product_id', 'menu_id',
                                                                              'category'])

        if not food_objs_record.empty:
            food_objs_record = food_objs_record.where((pd.notnull(food_objs_record)), None)
            food_objs_record['price'] = food_objs_record['price'].apply(lambda x: '${price}'.format(price=x) if x else None)
            food_objs_record = pd.pivot_table(food_objs_record,
                                              index=['product_id', 'menu_id', 'category'],
                                              columns=['tier'],
                                              values=['price'],
                                              aggfunc='first'
                                              )
            food_objs_record.columns = food_objs_record.columns.droplevel(0)
            food_objs_record.columns.name = None
            food_objs_record.reset_index(inplace=True)

            food_objs_record = food_objs_record \
                .join(food_objs_record_join.set_index(['product_id', 'menu_id', 'category']),
                      on=['product_id', 'menu_id', 'category'], how='left')

        if food_objs_record.empty:
            return pd.DataFrame(), 0

        # add empty columns
        tiers = food_objs_record.columns
        all_tiers = MenuTier.objects.filter(menu__name__exact=food_menu).values_list('tier', flat=True)
        all_tiers = [tier.lower() for tier in all_tiers]
        tier_none = [tier for tier in all_tiers if tier not in tiers]
        for tier in tier_none:
            food_objs_record[tier] = None

        num = len(food_objs_record)

        return food_objs_record, num

    @classmethod
    def get_price_tier(cls, center_type, product,
                       pagination=False, page_size=None, offset=None, filters=None, sort=None, order=None):

        if sort and order:
            if order == 'desc':
                sort = '-'+sort
        else:
            sort = 'category'

        product_ids = []
        if center_type == 'traditional' and product == 'bowling':
            product_ids = ProductChoice.retail_bowling_traditional_center
        elif center_type == 'experiential' and product == 'bowling':
            product_ids = ProductChoice.retail_bowling_experiential_center
        elif product == 'shoes':
            product_ids = ProductChoice.retail_shoe_product_ids

        pricing_tier = PricingTierTable.objects\
            .filter(
                    product_id__in=product_ids,
                    center_type=center_type
                    )

        if filters:
            filters = ast.literal_eval(filters)

            if filters.get('DOW'):
                pricing_tier = pricing_tier.filter(DOW__contains=filters['DOW'])
            if filters.get('time'):
                pricing_tier = pricing_tier.filter(time__contains=filters['time'])
            if filters.get('period_label'):
                pricing_tier = pricing_tier.filter(period_label=filters['period_label'])

        # num = pricing_tier.count()

        # if pagination:
        #     paginator = Paginator(pricing_tier, page_size,)
        #     current_page = int(offset/page_size) + 1
        #     pricing_tier = paginator.page(current_page).object_list

        pricing_tier_record = pd.DataFrame.from_records(pricing_tier.values(
                'DOW',
                'period_label',
                'time',
                'tier',
                'price',
                'order'
            ))

        if not pricing_tier_record.empty:
            pricing_tier_record['price'] = pricing_tier_record['price'].apply(lambda x: '${price}'.format(price=x))
            pricing_tier_record = pd.pivot_table(pricing_tier_record,
                                                 index=['DOW', 'time', 'period_label', 'order'],
                                                 columns=['tier'],
                                                 values=['price'],
                                                 aggfunc='first'
                                                 )
            pricing_tier_record.columns = pricing_tier_record.columns.droplevel(0)
            pricing_tier_record.columns.name = None
            pricing_tier_record.reset_index(inplace=True)
            pricing_tier_record.sort_values(by=['order'], inplace=True)

        if pricing_tier_record.empty:
            return pd.DataFrame(), 0

        pricing_tier_record.replace({'open': 'Open', 'cl': 'Cl'}, inplace=True, regex=True)

        num = len(pricing_tier_record)

        return pricing_tier_record, num

    @classmethod
    def get_tracking(cls, start, end, change_type,
                     pagination=False, page_size=None, offset=None, filters=None, sort=None, order=None):

        if sort and order:
            if order == 'desc':
                sort = '-' + sort
        else:
            sort = '-action_time'

        tracking_obj = Tracking.objects \
            .filter(action_time__range=[start, end]) \
            .order_by(sort)

        # if change_type:
        #     if change_type == 'retail bowling':
        #         tracking_type_id = ['1101', '2001', '3001']
        #     elif change_type == 'retail shoe':
        #         tracking_type_id = ['2002', '3002']
        #     elif change_type == 'retail food':
        #         tracking_type_id = ['2002', '3002']
        #     elif change_type == 'promos':
        #         tracking_type_id = ['2003', '3002']

        if filters:
            filters = ast.literal_eval(filters)

            if filters.get('tracking_id'):
                tracking_obj = tracking_obj.filter(tracking_id__exact=filters['tracking_id'])
            if filters.get('tracking_type'):
                tracking_obj = tracking_obj.filter(tracking_type__type__contains=filters['tracking_type'])
            if filters.get('action_time'):
                action_time = filters.get('action_time')
                regex = re.compile(r'(?P<month>\w{1,2})?/?(?P<day>\d{1,2})?/?(?P<year>\d{1,4})?\s*'
                                   r'(?P<hour>\d{1,2})?:?(?P<min>\d{1,2})?:?(?P<second>\d{1,2})?'
                                   )
                matched = regex.match(action_time)
                if matched:
                    matched = matched.groupdict()
                    matched = {k: v if v else '\d*' for k, v in matched.items()}
                    action_time = r'{year}-{month}-{day}\s*{hour}:{min}:{second}'.format(
                        year=matched['year'], month=matched['month'], day=matched['day'],
                        hour=matched['hour'], min=matched['min'], second=matched['second']
                    )
                else:
                    action_time = None
                tracking_obj = tracking_obj.filter(action_time__iregex=action_time)
            if filters.get('username'):
                tracking_obj = tracking_obj.filter(username__username__contains=filters['username'])
            if filters.get('input_params'):
                tracking_obj = tracking_obj.filter(input_params__contains=filters['input_params'])

        num = tracking_obj.count()

        if pagination:
            paginator = Paginator(tracking_obj, page_size,)
            current_page = int(offset/page_size) + 1
            tracking_obj = paginator.page(current_page).object_list

        tracking_record = pd.DataFrame.from_records(tracking_obj.values(
            'tracking_id',
            'tracking_type__type',
            'action_time',
            'username',
            'input_params'
        ))

        tracking_record.rename({'tracking_type__type': 'tracking_type'}, axis=1, inplace=True)
        tracking_record['tracking_type'] = tracking_record['tracking_type'].str.capitalize()

        if tracking_record.empty:
            return pd.DataFrame(), 0

        tracking_record['action_time'] = tracking_record['action_time']\
            .apply(lambda x: x.strftime('%m/%d/%y %H:%M:%S') if x else x)

        return tracking_record, num

    @classmethod
    def get_productopt_old(cls, date, pagination=False, page_size=None, offset=None, filters=None, sort=None,
                           order=None):

        if sort and order:
            if order == 'desc':
                sort = '-' + sort
        else:
            sort = 'center_id'

        center_obj = Centers.objects \
            .extra(select={'center_id': 'CAST(center_id AS INTEGER)'}) \
            .order_by(sort)

        if filters:
            filters = ast.literal_eval(filters)
            if filters.get('center_id'):
                center_obj = center_obj.filter(center_id__contains=filters['center_id'])
            if filters.get('center_name'):
                center_obj = center_obj.filter(center_name__contains=filters['center_name'])
            filters.pop('center_id', None)
            filters.pop('center_name', None)
            if filters:
                for key, value in filters.items():
                    key = key.split(',')
                    center_list = ProductOpt.objects  \
                        .filter(product_id__in=key,
                                opt__contains=value
                                ) \
                        .values_list('center_id__center_id', flat=True)
                    center_obj = center_obj.filter(center_id__in=center_list)

        num = center_obj.count()

        if pagination:
            paginator = Paginator(center_obj, page_size,)
            current_page = int(offset/page_size) + 1
            center_obj = paginator.page(current_page).object_list

        center_list = center_obj.values_list('center_id', flat=True)

        productopt_obj = ProductOpt.objects \
            .filter(center_id__center_id__in=center_list)

        productopt_record = pd.DataFrame.from_records(productopt_obj.values(
            'center_id__center_id',
            'center_id__center_name',
            'product_id',
            'opt'
        ))

        productopt_record.rename({
            'center_id__center_id': 'center_id',
            'center_id__center_name': 'center_name',
        }, axis=1, inplace=True)

        if productopt_record.empty:
            return pd.DataFrame(), 0

        productopt_record = pd.pivot_table(productopt_record,
                                           index=['center_id', 'center_name'],
                                           columns=['product_id'],
                                           values=['opt'],
                                           aggfunc='first',
                                           fill_value=None)

        productopt_record.columns = productopt_record.columns.droplevel(0)
        productopt_record.columns.name = None
        productopt_record.reset_index(inplace=True)

        for product_id in ['102', '103', '105', '106']:
            if not product_id in productopt_record.columns:
                productopt_record[product_id] = None

        productopt_record['102,105'] = productopt_record[['102', '105']].apply(lambda x: x['102'] or x['105'], axis=1)
        productopt_record['103,106'] = productopt_record[['103', '106']].apply(lambda x: x['103'] or x['106'], axis=1)
        # productopt_record.loc[
        #     productopt_record['product_id'].isin(ProductChoice.retail_bowling_prime_product_ids), 'product_name']\
        #     = 'Retail Prime Bowling'
        # productopt_record.loc[
        #     productopt_record['product_id'].isin(ProductChoice.retail_bowling_premium_product_ids), 'product_name']\
        #     = 'Retail Premium Bowling'

        # productopt_record['product_name'] = productopt_record['product_name'].str.capitalize()

        return productopt_record, num

    @classmethod
    def get_productopt(cls, date, pagination=False, page_size=None, offset=None, filters=None, sort=None,
                       order=None):

        if sort and order:
            if order == 'desc':
                sort = '-' + sort
        else:
            sort = 'center_id'

        center_obj = Centers.objects \
            .filter(status='open') \
            .extra(select={'center_id': 'CAST(center_id AS INTEGER)'}) \
            .order_by(sort)

        if filters:
            filters = ast.literal_eval(filters)

            for key, value in filters.items():
                filters_list = value.split(',')
                filters_list = [x.strip() for x in filters_list]
                filters[key] = filters_list
            if filters.get('center_id'):
                filter_item = filters.get('center_id')
                if len(filter_item) == 1:
                    center_obj = center_obj.filter(center_id__icontains=filter_item[0])
                else:
                    center_obj = center_obj.filter(center_id__in=filter_item)
            if filters.get('center_name'):
                filter_item = filters.get('center_name')
                if len(filter_item) == 1:
                    center_obj = center_obj.filter(center_name__icontains=filter_item[0])
                else:
                    center_obj = center_obj.filter(reduce(operator.or_,
                                                          (Q(center_name__icontains=item)
                                                           for item in filter_item if item)))

            # Filter by Opt in/out
            filters.pop('center_id', None)
            filters.pop('center_name', None)
            if filters:
                centers_opt = set()
                product_ids = filters.keys()
                center_list = center_obj.values_list('center_id', flat=True)
                productopt_records = ProductOptGet.get_productopt_bydate(product_ids, date, center_list)

                for key, value in filters.items():
                    productopt_records_opt = productopt_records[
                        (
                                (productopt_records['product_id'] == key) &
                                (productopt_records['opt'].str.contains(value[0], case=False))
                        )
                    ]
                    center_opt = productopt_records_opt['center_id'].unique().tolist()
                    if centers_opt:
                        centers_opt = set(centers_opt) & set(center_opt)
                    else:
                        centers_opt = center_opt
                # if centers_opt:
                centers_opt = list(centers_opt)
                center_obj = center_obj.filter(center_id__in=centers_opt)

        num = center_obj.count()

        if pagination:
            paginator = Paginator(center_obj, page_size,)
            current_page = int(offset/page_size) + 1
            center_obj = paginator.page(current_page).object_list

        center_list = center_obj.values_list('center_id', flat=True)
        center_list = [str(center_id) for center_id in center_list]

        if not center_list:
            return pd.DataFrame(), 0

        center_records = pd.DataFrame.from_records(center_obj.values('center_id', 'center_name'))
        center_records['center_id'] = center_records['center_id'].astype(str)

        products_list = Product.objects\
            .filter(report_type__in=['Retail Bowling', 'Retail Promos'], status='active', order__isnull=False) \
            .values_list('product_id', flat=True)
        # remove product_id
        remove_product_list = ['101', '102', '103', '104', '105', '106', '108', '109', '111', '112']
        products_list_final = [product_id for product_id in products_list if product_id not in remove_product_list]

        productopt_record = ProductOptGet.get_productopt(products_list_final, date, date, center_list)

        if not productopt_record.empty:
            productopt_record = pd.pivot_table(productopt_record,
                                               index=['center_id'],
                                               columns=['product_id'],
                                               values=['opt'],
                                               aggfunc='first',
                                               fill_value=None)

            productopt_record.columns = productopt_record.columns.droplevel(0)
            productopt_record.columns.name = None
            productopt_record.reset_index(inplace=True)

            center_records = center_records.join(productopt_record.set_index(['center_id']),
                                                 on=['center_id'], how='left')
        # add empty columns
        products_list_none = [product_id for product_id in products_list_final
                              if product_id not in list(center_records.columns)]
        for product_id in products_list_none:
            center_records[product_id] = None

        return center_records, num

    @classmethod
    def get_productschedule(cls, pagination=False, page_size=None, offset=None, filters=None, sort=None,
                            order=None):

        if sort and order:
            if order == 'desc':
                sort = '-' + sort
        else:
            sort = 'product_id'

        productschedule_obj = ProductSchedule.objects \
            .exclude(product_id__in=ProductChoice.retail_bowling_experiential_center) \
            .order_by(sort)

        if filters:
            pass
            # filters = ast.literal_eval(filters)
            # if filters.get('center_id'):
            #     center_obj = center_obj.filter(center_id__exact=filters['center_id'])
            # if filters.get('center_name'):
            #     center_obj = center_obj.filter(center_name__contains=filters['center_name'])

        num = productschedule_obj.count()

        if pagination:
            paginator = Paginator(productschedule_obj, page_size, )
            current_page = int(offset / page_size) + 1
            productschedule_obj = paginator.page(current_page).object_list

        productschedule_record = pd.DataFrame.from_records(productschedule_obj.values(
            'product_id__short_product_name',
            'product_id__product_id',
            'freq',
            'start',
            'end',
            'DOW'
        ))

        productschedule_record.rename({
            'product_id__short_product_name': 'product_name',
            'product_id__product_id': 'product_id',
        }, axis=1, inplace=True)

        if productschedule_record.empty:
            return pd.DataFrame(), 0

        for index, row in productschedule_record.iterrows():
            start = row['start']
            end = row['end']
            if row['freq'] == 'Weekly':
                if pd.isnull(start):
                    start = None
                elif start.year == 1900:
                    start = start.time()

                if pd.isnull(end):
                    end = None
                elif end.year == 1900:
                    end = end.time()

                productschedule_record.at[index, 'start'] = start
                productschedule_record.at[index, 'end'] = end

        return productschedule_record, num

    @classmethod
    def get_bs_change_report(cls, start, end, eff_start, eff_end, products_id=None,
                             pagination=False, page_size=None, offset=None, filters=None, sort=None, order=None):

        if sort and order:
            if order == 'desc':
                sort = '-' + sort
        else:
            sort = '-action_time'

        change_report_obj = BSChangeReport.objects \
            .all() \
            .order_by(sort)

        if products_id:
            change_report_obj = change_report_obj.filter(product_id__in=products_id)

        # print(pd.DataFrame.from_records(change_report_obj.values()))
        # print(start, type(start))
        if start:
            change_report_obj = change_report_obj.filter(action_time__gte=start)
        if end:
            change_report_obj = change_report_obj.filter(action_time__lte=end)
        if eff_start:
            change_report_obj = change_report_obj.filter(effective_end__gte=eff_start)
        if eff_end:
            change_report_obj = change_report_obj.filter(effective_start__lte=eff_end)

        if filters:
            filters = ast.literal_eval(filters)

            for key, value in filters.items():
                filters_list = value.split(',')
                filters_list = [x.strip() for x in filters_list]
                filters[key] = filters_list
            if filters.get('center_id'):
                filter_item = filters.get('center_id')
                if len(filter_item) == 1:
                    change_report_obj = change_report_obj.filter(center_id__center_id__icontains=filter_item[0])
                else:
                    change_report_obj = change_report_obj.filter(center_id__center_id__in=filter_item)
            if filters.get('center_name'):
                filter_item = filters.get('center_name')
                if len(filter_item) == 1:
                    change_report_obj = change_report_obj.filter(center_id__center_name__icontains=filter_item[0])
                else:
                    change_report_obj = change_report_obj.filter(reduce(operator.or_,
                                                                        (Q(center_id__center_name__icontains=item)
                                                                         for item in filter_item if item)))
            if filters.get('tracking_id'):
                filter_item = filters.get('tracking_id')
                if len(filter_item) == 1:
                    change_report_obj = change_report_obj.filter(tracking_id__tracking_id__icontains=filter_item[0])
                else:
                    change_report_obj = change_report_obj.filter(tracking_id__tracking_id__in=filter_item)
            if filters.get('action_time'):
                action_time = filters.get('action_time')
                action_time = action_time[0] if action_time else ''
                regex = re.compile(r'(?P<month>\w{1,2})?/?(?P<day>\d{1,2})?/?(?P<year>\d{1,4})?\s*'
                                   r'(?P<hour>\d{1,2})?:?(?P<min>\d{1,2})?:?(?P<second>\d{1,2})?'
                                   )
                matched = regex.match(action_time)
                if matched:
                    matched = matched.groupdict()
                    matched = {k: v if v else '\d*' for k, v in matched.items()}
                    action_time = r'20{year}-{month}-{day}\s*{hour}:{min}:{second}'.format(
                        year=matched['year'], month=matched['month'], day=matched['day'],
                        hour=matched['hour'], min=matched['min'], second=matched['second']
                    )
                else:
                    action_time = None
                change_report_obj = change_report_obj.filter(action_time__iregex=action_time)
            if filters.get('product_num'):
                filter_item = filters.get('product_num')
                if len(filter_item) == 1:
                    change_report_obj = change_report_obj.filter(product_id__product_num__icontains=filter_item[0])
                else:
                    change_report_obj = change_report_obj.filter(product_id__product_num__in=filter_item)
            if filters.get('username'):
                filter_item = filters.get('username')
                if len(filter_item) == 1:
                    change_report_obj = change_report_obj.filter(username__username__icontains=filter_item[0])
                else:
                    change_report_obj = change_report_obj.filter(reduce(operator.or_,
                                                                        (Q(username__username__icontains=item)
                                                                         for item in filter_item if item)))
            if filters.get('effective_start'):
                effective_start = filters.get('effective_start')
                effective_start = effective_start[0] if effective_start else ''
                regex = re.compile(r'(?P<month>\w{1,2})?/?(?P<day>\d{1,2})?/?(?P<year>\d{1,4})?\s*')
                matched = regex.match(effective_start)
                if matched:
                    matched = matched.groupdict()
                    matched = {k: v if v else '\d*' for k, v in matched.items()}
                    effective_start = r'20{year}-{month}-{day}\s*'.format(
                        year=matched['year'], month=matched['month'], day=matched['day'])
                else:
                    effective_start = None
                change_report_obj = change_report_obj.filter(effective_start__iregex=effective_start)
            if filters.get('effective_end'):
                effective_end = filters.get('effective_end')
                effective_start = effective_end[0] if effective_end else ''
                regex = re.compile(r'(?P<month>\w{1,2})?/?(?P<day>\d{1,2})?/?(?P<year>\d{1,4})?\s*')
                matched = regex.match(effective_end)
                if matched:
                    matched = matched.groupdict()
                    matched = {k: v if v else '\d*' for k, v in matched.items()}
                    effective_end = r'20{year}-{month}-{day}\s*'.format(
                        year=matched['year'], month=matched['month'], day=matched['day'])
                else:
                    effective_end = None
                change_report_obj = change_report_obj.filter(effective_end__iregex=effective_end)
            if filters.get('product'):
                filter_item = filters.get('product')
                if len(filter_item) == 1:
                    change_report_obj = change_report_obj.filter(product_id__product_name__icontains=filter_item[0])
                else:
                    change_report_obj = change_report_obj.filter(reduce(operator.or_,
                                                                        (Q(product_id__product_name__icontains=item)
                                                                         for item in filter_item if item)))
            if filters.get('price_old'):
                change_report_obj = change_report_obj.filter(price_old__contains=filters['price_old'])
            if filters.get('price_new'):
                change_report_obj = change_report_obj.filter(price_new__contains=filters['price_new'])
            if filters.get('is_bulk_change'):
                change_report_obj = change_report_obj.filter(is_bulk_change__exact=filters['is_bulk_change'])

        num = change_report_obj.count()

        if pagination:
            paginator = Paginator(change_report_obj, page_size, )
            current_page = int(offset / page_size) + 1
            change_report_obj = paginator.page(current_page).object_list

        change_report_record = pd.DataFrame.from_records(change_report_obj.values(
            'center_id',
            'center_id__center_name',
            'tracking_id',
            'action_time',
            'username',
            'product_id__report_type',
            'effective_start',
            'effective_end',
            'product_id__readable_product_name',
            'product_id__product_num',
            'price_old',
            'price_new',
            'opt',
            'is_bulk_change'
        ))

        if change_report_record.empty:
            return pd.DataFrame(), 0

        change_report_record.rename({'product_id__readable_product_name': 'product',
                                     'product_id__product_num': 'product_num',
                                     'product_id__report_type': 'report_type',
                                     'center_id__center_name': 'center_name'
                                     },
                                    axis=1, inplace=True)
        change_report_record['is_bulk_change'] = change_report_record['is_bulk_change'].astype(str)

        # date format change
        change_report_record['effective_start'] = change_report_record['effective_start']\
            .apply(lambda x: x.strftime('%m/%d/%y') if x else x)
        change_report_record['effective_end'] = change_report_record['effective_end']\
            .apply(lambda x: x.strftime('%m/%d/%y') if x else x)
        change_report_record['action_time'] = change_report_record['action_time']\
            .apply(lambda x: x.strftime('%m/%d/%y %H:%M:%S') if x else x)
        # change_report_record['product'] = change_report_record['product'].str.capitalize()

        return change_report_record, num

    @classmethod
    def get_food_change_report(cls, start, end, eff_start, eff_end,
                               pagination=False, page_size=None, offset=None, filters=None, sort=None, order=None):

        if sort and order:
            if order == 'desc':
                sort = '-' + sort
        else:
            sort = '-action_time'

        change_report_obj = FoodChangeReport.objects \
            .all() \
            .order_by(sort)

        # print(pd.DataFrame.from_records(change_report_obj.values()))
        # print(start, type(start))
        if start:
            change_report_obj = change_report_obj.filter(action_time__gte=start)
        if end:
            change_report_obj = change_report_obj.filter(action_time__lte=end)
        if eff_start:
            change_report_obj = change_report_obj.filter(effective_end__gte=eff_start)
        if eff_end:
            change_report_obj = change_report_obj.filter(effective_start__lte=eff_end)

        if filters:
            filters = ast.literal_eval(filters)

            for key, value in filters.items():
                filters_list = value.split(',')
                filters_list = [x.strip() for x in filters_list]
                filters[key] = filters_list
            if filters.get('center_id'):
                filter_item = filters.get('center_id')
                if len(filter_item) == 1:
                    change_report_obj = change_report_obj.filter(center_id__center_id__icontains=filter_item[0])
                else:
                    change_report_obj = change_report_obj.filter(center_id__center_id__in=filter_item)
            if filters.get('tracking_id'):
                filter_item = filters.get('tracking_id')
                if len(filter_item) == 1:
                    change_report_obj = change_report_obj.filter(tracking_id__tracking_id__icontains=filter_item[0])
                else:
                    change_report_obj = change_report_obj.filter(tracking_id__tracking_id__in=filter_item)
            if filters.get('action_time'):
                filter_item = filters.get('action_time')
                if len(filter_item) == 1:
                    change_report_obj = change_report_obj.filter(action_time__icontains=filter_item[0])
                else:
                    change_report_obj = change_report_obj.filter(reduce(operator.or_, (Q(action_time__icontains=item) for item in filter_item if item)))
            if filters.get('username'):
                filter_item = filters.get('username')
                if len(filter_item) == 1:
                    change_report_obj = change_report_obj.filter(username__username__icontains=filter_item[0])
                else:
                    change_report_obj = change_report_obj.filter(reduce(operator.or_, (Q(username__username__icontains=item) for item in filter_item if item)))
            if filters.get('product_start'):
                filter_item = filters.get('product_start')
                if len(filter_item) == 1:
                    change_report_obj = change_report_obj.filter(product_start__icontains=filter_item[0])
                else:
                    change_report_obj = change_report_obj.filter(reduce(operator.or_, (Q(product_start__icontains=item) for item in filter_item if item)))
            if filters.get('product_end'):
                filter_item = filters.get('product_end')
                if len(filter_item) == 1:
                    change_report_obj = change_report_obj.filter(product_end__icontains=filter_item[0])
                else:
                    change_report_obj = change_report_obj.filter(reduce(operator.or_, (Q(product_end__icontains=item) for item in filter_item if item)))
            if filters.get('product'):
                filter_item = filters.get('product')
                if len(filter_item) == 1:
                    change_report_obj = change_report_obj.filter(product_id__product_name__icontains=filter_item[0])
                else:
                    change_report_obj = change_report_obj.filter(reduce(operator.or_, (Q(product_id__product_name__icontains=item) for item in filter_item if item)))
            if filters.get('prod_num'):
                filter_item = filters.get('prod_num')
                if len(filter_item) == 1:
                    change_report_obj = change_report_obj.filter(product_id__product_id__icontains=filter_item[0])
                else:
                    change_report_obj = change_report_obj.filter(product_id__product_id__in=filter_item)
            if filters.get('category'):
                filter_item = filters.get('category')
                if len(filter_item) == 1:
                    change_report_obj = change_report_obj.filter(category__icontains=filter_item[0])
                else:
                    change_report_obj = change_report_obj.filter(category__in=filter_item)
            if filters.get('price_old'):
                filter_item = filters.get('price_old')
                if len(filter_item) == 1:
                    change_report_obj = change_report_obj.filter(price_old__icontains=filter_item[0])
                else:
                    change_report_obj = change_report_obj.filter(reduce(operator.or_, (Q(price_old__icontains=item) for item in filter_item if item)))
            if filters.get('price_new'):
                filter_item = filters.get('price_new')
                if len(filter_item) == 1:
                    change_report_obj = change_report_obj.filter(price_new__icontains=filter_item[0])
                else:
                    change_report_obj = change_report_obj.filter(reduce(operator.or_, (Q(price_new__icontains=item) for item in filter_item if item)))
            if filters.get('tier'):
                filter_item = filters.get('tier')
                if len(filter_item) == 1:
                    change_report_obj = change_report_obj.filter(tier__icontains=filter_item[0])
                else:
                    change_report_obj = change_report_obj.filter(reduce(operator.or_, (Q(tier__icontains=item) for item in filter_item if item)))
            if filters.get('menu'):
                filter_item = filters.get('menu')
                if len(filter_item) == 1:
                    change_report_obj = change_report_obj.filter(Q(menu_id__name__icontains=filter_item[0]) | Q(menu_id2__menu_name__icontains=filter_item[0]))
                else:
                    change_report_obj = change_report_obj.filter(Q(reduce(operator.or_, (Q(menu_id__name__icontains=item) for item in filter_item if item))) |
                                                                 Q(reduce(operator.or_, (Q(menu_id2__menu_name__icontains=item) for item in filter_item if item)))
                                                                 )
            if filters.get('description'):
                filter_item = filters.get('description')
                if len(filter_item) == 1:
                    change_report_obj = change_report_obj.filter(description__icontains=filter_item[0])
                else:
                    change_report_obj = change_report_obj.filter(reduce(operator.or_, (Q(description__icontains=item) for item in filter_item if item)))


            # if filters.get('tracking_id'):
            #     change_report_obj = change_report_obj.filter(tracking_id__tracking_id__exact=filters['tracking_id'])
            # if filters.get('action_time'):
            #     change_report_obj = change_report_obj.filter(action_time__contains=filters['action_time'])
            # if filters.get('username'):
            #     change_report_obj = change_report_obj.filter(username__username__contains=filters['username'])
            # if filters.get('product_start'):
            #     change_report_obj = change_report_obj.filter(product_start__contains=filters['product_start'])
            # if filters.get('product_end'):
            #     change_report_obj = change_report_obj.filter(product_end__contains=filters['product_end'])
            # if filters.get('product_name'):
            #     change_report_obj = change_report_obj.filter(product_id__product_name__contains=filters['product_name'])
            # if filters.get('prod_num'):
            #     change_report_obj = change_report_obj.filter(product_id__product_num__contains=filters['prod_num'])
            # if filters.get('price_old'):
            #     change_report_obj = change_report_obj.filter(price_old__contains=filters['price_old'])
            # if filters.get('price_new'):
            #     change_report_obj = change_report_obj.filter(price_new__contains=filters['price_new'])
            # if filters.get('tier'):
            #     change_report_obj = change_report_obj.filter(tier__contains=filters['tier'])
            # if filters.get('menu'):
            #     change_report_obj = change_report_obj.filter(menu_id__name__contains=filters['tier'])
            # if filters.get('description'):
            #     change_report_obj = change_report_obj.filter(description__contains=filters['description'])

        num = change_report_obj.count()

        if pagination:
            paginator = Paginator(change_report_obj, page_size, )
            current_page = int(offset / page_size) + 1
            change_report_obj = paginator.page(current_page).object_list

        change_report_record = pd.DataFrame.from_records(change_report_obj.values(
            'tracking_id',
            'action_time',
            'username',
            'center_id',
            'product_id__product_name',
            'product_id__product_num',
            'tier',
            'menu_id__name',
            'menu_id2__menu_name',
            'category',
            'product_start',
            'product_end',
            'price_old',
            'price_new',
            'description'
        ))

        if change_report_record.empty:
            return pd.DataFrame(), 0

        change_report_record.rename({'product_id__product_name': 'product',
                                     'product_id__product_num': 'prod_num',
                                     'menu_id__name': 'menu',
                                     'menu_id2__menu_name': 'menu2'
                                     },
                                    axis=1, inplace=True)

        change_report_record['menu'] = change_report_record[['menu', 'menu2']]\
            .apply(lambda x: x['menu'] if x['menu'] else x['menu2'], axis=1)
        # change_report_record['product'] = change_report_record['product'].str.capitalize()

        return change_report_record, num

    @classmethod
    def get_alcohol_change_report(cls, start, end, eff_start, eff_end,
                                  pagination=False, page_size=None, offset=None, filters=None, sort=None, order=None):

        if sort and order:
            if order == 'desc':
                sort = '-' + sort
        else:
            sort = '-action_time'

        change_report_obj = AlcoholChangeReport.objects \
            .all() \
            .order_by(sort)

        # print(pd.DataFrame.from_records(change_report_obj.values()))
        # print(start, type(start))
        if start:
            change_report_obj = change_report_obj.filter(action_time__gte=start)
        if end:
            change_report_obj = change_report_obj.filter(action_time__lte=end)
        if eff_start:
            change_report_obj = change_report_obj.filter(effective_end__gte=eff_start)
        if eff_end:
            change_report_obj = change_report_obj.filter(effective_start__lte=eff_end)

        if filters:
            filters = ast.literal_eval(filters)

            if filters.get('tracking_id'):
                change_report_obj = change_report_obj.filter(tracking_id__tracking_id__exact=filters['tracking_id'])
            if filters.get('action_time'):
                action_time = filters.get('action_time')
                regex = re.compile(r'(?P<month>\w{1,2})?/?(?P<day>\d{1,2})?/?(?P<year>\d{1,4})?\s*'
                                   r'(?P<hour>\d{1,2})?:?(?P<min>\d{1,2})?:?(?P<second>\d{1,2})?'
                                   )
                matched = regex.match(action_time)
                if matched:
                    matched = matched.groupdict()
                    matched = {k: v if v else '\d*' for k, v in matched.items()}
                    action_time = r'{year}-{month}-{day}\s*{hour}:{min}:{second}'.format(
                        year=matched['year'], month=matched['month'], day=matched['day'],
                        hour=matched['hour'], min=matched['min'], second=matched['second']
                    )
                else:
                    action_time = None
                change_report_obj = change_report_obj.filter(action_time__iregex=action_time)
            if filters.get('username'):
                change_report_obj = change_report_obj.filter(username__username__contains=filters['username'])
            if filters.get('start'):
                start = filters.get('start')
                regex = re.compile(r'(?P<month>\w{1,2})?/?(?P<day>\d{1,2})?/?(?P<year>\d{1,4})?\s*')
                matched = regex.match(start)
                if matched:
                    matched = matched.groupdict()
                    matched = {k: v if v else '\d*' for k, v in matched.items()}
                    start = r'{year}-{month}-{day}\s*'.format(
                        year=matched['year'], month=matched['month'], day=matched['day'])
                else:
                    start = None
                change_report_obj = change_report_obj.filter(start__iregex=start)
            if filters.get('end'):
                end = filters.get('end')
                regex = re.compile(r'(?P<month>\w{1,2})?/?(?P<day>\d{1,2})?/?(?P<year>\d{1,4})?\s*')
                matched = regex.match(end)
                if matched:
                    matched = matched.groupdict()
                    matched = {k: v if v else '\d*' for k, v in matched.items()}
                    end = r'{year}-{month}-{day}\s*'.format(
                        year=matched['year'], month=matched['month'], day=matched['day'])
                else:
                    end = None
                change_report_obj = change_report_obj.filter(end__iregex=end)
            if filters.get('product_id'):
                change_report_obj = change_report_obj.filter(product_id__contains=filters['product_id'])
            if filters.get('product_name'):
                change_report_obj = change_report_obj\
                    .filter(product_id__product_name__contains=filters['product_name'])
            if filters.get('price_old'):
                change_report_obj = change_report_obj.filter(price_old__contains=filters['price_old'])
            if filters.get('price_new'):
                change_report_obj = change_report_obj.filter(price_new__contains=filters['price_new'])
            if filters.get('tier'):
                change_report_obj = change_report_obj.filter(tier__contains=filters['tier'])
            if filters.get('menu'):
                change_report_obj = change_report_obj.filter(menu__contains=filters['tier'])
            if filters.get('category'):
                change_report_obj = change_report_obj.filter(menu__contains=filters['category'])
            if filters.get('level'):
                change_report_obj = change_report_obj.filter(menu__contains=filters['level'])
            if filters.get('description'):
                change_report_obj = change_report_obj.filter(description__contains=filters['description'])

        num = change_report_obj.count()

        if pagination:
            paginator = Paginator(change_report_obj, page_size, )
            current_page = int(offset / page_size) + 1
            change_report_obj = paginator.page(current_page).object_list

        change_report_record = pd.DataFrame.from_records(change_report_obj.values(
            'tracking_id',
            'action_time',
            'username',
            'product_id',
            'product_id__product_name',
            'menu',
            'category',
            'level',
            'tier',
            'start',
            'end',
            'price_old',
            'price_new',
            'description'
        ))

        if change_report_record.empty:
            return pd.DataFrame(), 0

        change_report_record.rename({
                                     'product_id__product_num': 'prod_num',
                                     },
                                    axis=1, inplace=True)


        # date format change
        change_report_record['start'] = change_report_record['start']\
            .apply(lambda x: x.strftime('%m/%d/%y') if x else x)
        change_report_record['end'] = change_report_record['end'].apply(lambda x: x.strftime('%m/%d/%y') if x else x)
        change_report_record['action_time'] = change_report_record['action_time']\
            .apply(lambda x: x.strftime('%m/%d/%y %H:%M:%S') if x else x)
        # change_report_record['product'] = change_report_record['product'].str.capitalize()

        return change_report_record, num

    @classmethod
    def get_event_change_report(cls, start, end, eff_start, eff_end, products_id=None,
                                pagination=False, page_size=None, offset=None, filters=None, sort=None, order=None):

        if sort and order:
            if order == 'desc':
                sort = '-' + sort
        else:
            sort = '-action_time'

        change_report_obj = EventChangeReport.objects \
            .all() \
            .order_by(sort)

        # if products_id:
        #     change_report_obj = change_report_obj.filter(product_id__in=products_id)

        # print(pd.DataFrame.from_records(change_report_obj.values()))
        # print(start, type(start))
        if start:
            change_report_obj = change_report_obj.filter(action_time__gte=start)
        if end:
            change_report_obj = change_report_obj.filter(action_time__lte=end)
        if eff_start:
            change_report_obj = change_report_obj.filter(effective_end__gte=eff_start)
        if eff_end:
            change_report_obj = change_report_obj.filter(effective_start__lte=eff_end)

        if filters:
            filters = ast.literal_eval(filters)

            for key, value in filters.items():
                filters_list = value.split(',')
                filters_list = [x.strip() for x in filters_list]
                filters[key] = filters_list
            if filters.get('center_id'):
                filter_item = filters.get('center_id')
                if len(filter_item) == 1:
                    change_report_obj = change_report_obj.filter(center_id__center_id__icontains=filter_item[0])
                else:
                    change_report_obj = change_report_obj.filter(center_id__center_id__in=filter_item)
            if filters.get('center_name'):
                filter_item = filters.get('center_name')
                if len(filter_item) == 1:
                    change_report_obj = change_report_obj.filter(center_id__center_name__icontains=filter_item[0])
                else:
                    change_report_obj = change_report_obj.filter(reduce(operator.or_,
                                                                        (Q(center_id__center_name__icontains=item)
                                                                         for item in filter_item if item)))
            if filters.get('tracking_id'):
                filter_item = filters.get('tracking_id')
                if len(filter_item) == 1:
                    change_report_obj = change_report_obj.filter(tracking_id__tracking_id__icontains=filter_item[0])
                else:
                    change_report_obj = change_report_obj.filter(tracking_id__tracking_id__in=filter_item)
            if filters.get('action_time'):
                action_time = filters.get('action_time')
                regex = re.compile(r'(?P<month>\w{1,2})?/?(?P<day>\d{1,2})?/?(?P<year>\d{1,4})?\s*'
                                   r'(?P<hour>\d{1,2})?:?(?P<min>\d{1,2})?:?(?P<second>\d{1,2})?'
                                   )
                matched = regex.match(action_time)
                if matched:
                    matched = matched.groupdict()
                    matched = {k: v if v else '\d*' for k, v in matched.items()}
                    action_time = r'{year}-{month}-{day}\s*{hour}:{min}:{second}'.format(
                        year=matched['year'], month=matched['month'], day=matched['day'],
                        hour=matched['hour'], min=matched['min'], second=matched['second']
                    )
                else:
                    action_time = None
                change_report_obj = change_report_obj.filter(action_time__iregex=action_time)
            if filters.get('product_num'):
                filter_item = filters.get('product_num')
                if len(filter_item) == 1:
                    change_report_obj = change_report_obj.filter(product_id__product_num__icontains=filter_item[0])
                else:
                    change_report_obj = change_report_obj.filter(product_id__product_num__in=filter_item)
            if filters.get('username'):
                filter_item = filters.get('username')
                if len(filter_item) == 1:
                    change_report_obj = change_report_obj.filter(username__username__icontains=filter_item[0])
                else:
                    change_report_obj = change_report_obj.filter(reduce(operator.or_,
                                                                        (Q(username__username__icontains=item)
                                                                         for item in filter_item if item)))
            if filters.get('effective_start'):
                effective_start = filters.get('effective_start')
                regex = re.compile(r'(?P<month>\w{1,2})?/?(?P<day>\d{1,2})?/?(?P<year>\d{1,4})?\s*')
                matched = regex.match(effective_start)
                if matched:
                    matched = matched.groupdict()
                    matched = {k: v if v else '\d*' for k, v in matched.items()}
                    effective_start = r'{year}-{month}-{day}\s*'.format(
                        year=matched['year'], month=matched['month'], day=matched['day'])
                else:
                    effective_start = None
                change_report_obj = change_report_obj.filter(effective_start__iregex=effective_start)
            if filters.get('effective_end'):
                effective_end = filters.get('effective_end')
                regex = re.compile(r'(?P<month>\w{1,2})?/?(?P<day>\d{1,2})?/?(?P<year>\d{1,4})?\s*')
                matched = regex.match(effective_end)
                if matched:
                    matched = matched.groupdict()
                    matched = {k: v if v else '\d*' for k, v in matched.items()}
                    effective_end = r'{year}-{month}-{day}\s*'.format(
                        year=matched['year'], month=matched['month'], day=matched['day'])
                else:
                    effective_end = None
                change_report_obj = change_report_obj.filter(effective_end__iregex=effective_end)
            if filters.get('product_RMPS'):
                filter_item = filters.get('product_RMPS')
                if len(filter_item) == 1:
                    change_report_obj = change_report_obj.filter(product_RMPS__icontains=filter_item[0])
                else:
                    change_report_obj = change_report_obj.filter(reduce(operator.or_,
                                                                        (Q(product_RMPS__icontains=item)
                                                                         for item in filter_item if item)))
            if filters.get('price_old'):
                change_report_obj = change_report_obj.filter(price_old__contains=filters['price_old'])
            if filters.get('price_new'):
                change_report_obj = change_report_obj.filter(price_new__contains=filters['price_new'])
            # if filters.get('is_bulk_change'):
            #     change_report_obj = change_report_obj.filter(is_bulk_change__exact=filters['is_bulk_change'])

        num = change_report_obj.count()

        if pagination:
            paginator = Paginator(change_report_obj, page_size, )
            current_page = int(offset / page_size) + 1
            change_report_obj = paginator.page(current_page).object_list

        change_report_record = pd.DataFrame.from_records(change_report_obj.values(
            'center_id',
            'center_id__center_name',
            'tracking_id',
            'action_time',
            'username',
            # 'product_id__report_type',
            # 'effective_start',
            # 'effective_end',
            # 'product_id__readable_product_name',
            # 'product_id__product_num',
            'product_RMPS',
            'price_old',
            'price_new',
            # 'opt',
            # 'is_bulk_change'
        ))

        if change_report_record.empty:
            return pd.DataFrame(), 0

        change_report_record.rename({
            # 'product_id__readable_product_name': 'product',
            # 'product_id__product_num': 'product_num',
            # 'product_id__report_type': 'report_type',
            'center_id__center_name': 'center_name'
            }, axis=1, inplace=True)
        # change_report_record['is_bulk_change'] = change_report_record['is_bulk_change'].astype(str)

        # date format change
        # change_report_record['effective_start'] = change_report_record['effective_start']\
        #     .apply(lambda x: x.strftime('%m/%d/%y') if x else x)
        # change_report_record['effective_end'] = change_report_record['effective_end']\
        #     .apply(lambda x: x.strftime('%m/%d/%y') if x else x)
        change_report_record['action_time'] = change_report_record['action_time']\
            .apply(lambda x: x.strftime('%m/%d/%y %H:%M:%S') if x else x)
        # change_report_record['product'] = change_report_record['product'].str.capitalize()

        return change_report_record, num

    @classmethod
    def get_email_log(cls, start, end, eff_start, eff_end,
                      pagination=False, page_size=None, offset=None, filters=None, sort=None, order=None):

        if sort and order:
            if order == 'desc':
                sort = '-' + sort
        else:
            sort = '-action_time'

        email_log_obj = EmailNoticeLog.objects \
            .all() \
            .order_by(sort)

        # print(pd.DataFrame.from_records(email_log_obj.values()))
        # print(start, type(start))
        if start:
            email_log_obj = email_log_obj.filter(action_time__gte=start)
        if end:
            email_log_obj = email_log_obj.filter(action_time__lte=end)
        # if eff_start:
        #     email_log_obj = email_log_obj.filter(effective_end__gte=eff_start)
        # if eff_end:
        #     email_log_obj = email_log_obj.filter(effective_start__lte=eff_end)

        if filters:
            filters = ast.literal_eval(filters)

            if filters.get('notice_name'):
                email_log_obj = email_log_obj.filter(notice_type_id__notice_name__contains=filters['notice_name'])
            if filters.get('username'):
                email_log_obj = email_log_obj.filter(username__username__contains=filters['username'])
            if filters.get('action_time'):
                action_time = filters.get('action_time')
                regex = re.compile(r'(?P<month>\w{1,2})?/?(?P<day>\d{1,2})?/?(?P<year>\d{1,4})?\s*'
                                   r'(?P<hour>\d{1,2})?:?(?P<min>\d{1,2})?:?(?P<second>\d{1,2})?'
                                   )
                matched = regex.match(action_time)
                if matched:
                    matched = matched.groupdict()
                    matched = {k: v if v else '\d*' for k, v in matched.items()}
                    action_time = r'{year}-{month}-{day}\s*{hour}:{min}:{second}'.format(
                        year=matched['year'], month=matched['month'], day=matched['day'],
                        hour=matched['hour'], min=matched['min'], second=matched['second']
                    )
                else:
                    action_time = None
                email_log_obj = email_log_obj.filter(action_time__iregex=action_time)
            if filters.get('subject'):
                email_log_obj = email_log_obj.filter(subject__contains=filters['subject'])
            if filters.get('content'):
                email_log_obj = email_log_obj.filter(content__contains=filters['content'])

        num = email_log_obj.count()

        if pagination:
            paginator = Paginator(email_log_obj, page_size, )
            current_page = int(offset / page_size) + 1
            email_log_obj = paginator.page(current_page).object_list

        email_log_record = pd.DataFrame.from_records(email_log_obj.values(
            'notice_type_id__notice_name',
            'username',
            'action_time',
            'subject',
            'content',
        ))

        if email_log_record.empty:
            return pd.DataFrame(), 0

        email_log_record.rename({'notice_type_id__notice_name': 'notice_name'}, axis=1, inplace=True)
        email_log_record['content'] = email_log_record['content'].apply(lambda x: strip_tags(x))
        email_log_record['action_time'] = email_log_record['action_time']\
            .apply(lambda x: x.strftime('%m/%d/%y %H:%M:%S') if x else x)

        return email_log_record, num

    class LastPrice:

        @classmethod
        def get_last_price(cls, product_ids, center_ids=None, as_of_date=None, perpetual_only=False):
            if not as_of_date:
                as_of_date = UDatetime.now_local().date()
            # as_of_date_eow = as_of_date - td(days=as_of_date.weekday()) + td(days=6)

            # Find by last price
            if set(product_ids) & set(ProductChoice.retail_bowling_ids_new):
                retail_bowling_price_obj = RetailBowlingPrice.objects \
                    .filter(product_id__product_id__in=product_ids,
                            date__range=[as_of_date - datetime.timedelta(days=360), as_of_date]
                            )
                if center_ids:
                    retail_bowling_price_obj = retail_bowling_price_obj.filter(center_id__in=list(center_ids))
                if perpetual_only:
                    retail_bowling_price_obj = retail_bowling_price_obj.filter(perpetual=True)
            else:
                retail_bowling_price_obj = RetailBowlingPrice.objects.none()

            if set(product_ids) & set(ProductChoice.retail_shoe_product_ids_new):
                shoe_price_obj = RetailShoePrice.objects \
                    .filter(product_id__product_id__in=product_ids,
                            date__range=[as_of_date - datetime.timedelta(days=360), as_of_date]
                            )
                if center_ids:
                    shoe_price_obj = shoe_price_obj.filter(center_id__in=list(center_ids))
                if perpetual_only:
                    shoe_price_obj = shoe_price_obj.filter(perpetual=True)
            else:
                shoe_price_obj = RetailShoePrice.objects.none()

            product_ids_product = [id for id in product_ids if id not in ProductChoice.retail_bowling_ids_new]
            product_ids_product = [id for id in product_ids_product if id not in ProductChoice.retail_shoe_product_ids]

            if product_ids_product:
                product_price_obj = ProductPrice.objects \
                    .filter(product_id__product_id__in=product_ids_product,
                            date__range=[as_of_date - datetime.timedelta(days=360), as_of_date]
                            )
                if center_ids:
                    product_price_obj = product_price_obj.filter(center_id__in=list(center_ids))
                if perpetual_only:
                    product_price_obj = product_price_obj.filter(perpetual=True)
            else:
                product_price_obj = ProductPrice.objects.none()

            # Combine records
            if retail_bowling_price_obj.exists():
                retail_bowling_price_records = pd.DataFrame\
                    .from_records(retail_bowling_price_obj
                                  .values('date', 'center_id', 'product_id', 'price'))
            else:
                retail_bowling_price_records = pd.DataFrame()

            if shoe_price_obj.exists():
                shoe_price_records = pd.DataFrame \
                    .from_records(shoe_price_obj
                                  .values('date', 'center_id', 'product_id', 'price'))
            else:
                shoe_price_records = pd.DataFrame()

            if product_price_obj.exists():
                product_price_records = pd.DataFrame \
                    .from_records(product_price_obj
                                  .values('date', 'center_id', 'product_id', 'price'))
            else:
                product_price_records = pd.DataFrame()

            concat_records = pd.concat([retail_bowling_price_records,
                                        shoe_price_records,
                                        product_price_records],
                                        ignore_index=True
                                       )

            # def latest_price(x):
            #     print(x)
            #     x.sort_values(['date'], inplace=True)
            #     x = x.iloc[-1, :]
            #     return x['price']
            #
            # result_records = pd.DataFrame(concat_records
            #                               .groupby(['center_id', 'product_id'])
            #                               .apply(latest_price), columns=['price'])
            # result_records.reset_index(inplace=True)

            # get result
            if not center_ids:
                center_list = Centers.objects.all().values_list('center_id', 'center_type', 'bowling_tier')
            else:
                center_list = Centers.objects.filter(center_id__in=center_ids) \
                    .values_list('center_id', 'center_type', 'bowling_tier')

            center_product_list = [
                {'center_id': center_id,
                 'product_id': product_id,
                 'center_type': center_type,
                 'bowling_tier': bowling_tier
                 }
                for center_id, center_type, bowling_tier in center_list for product_id in product_ids
            ]
            result_records = pd.DataFrame(center_product_list)

            # join last price
            if not concat_records.empty:
                concat_records = concat_records \
                    .sort_values(['center_id', 'product_id', 'date']) \
                    .drop_duplicates(['center_id', 'product_id'], keep='last') \
                    .drop(['date'], axis=1)
                result_records = result_records.join(concat_records.set_index(['center_id', 'product_id']),
                                                 on=['center_id', 'product_id'], how='left')
            else:
                result_records['price'] = None

            # add tier table price
            if as_of_date >= dt(2017, 12, 15).date():
                result_records_na = result_records[(result_records['price'].isna()) &
                                                   (result_records['product_id']
                                                    .isin(ProductChoice.retail_bowling_ids_new +
                                                          ProductChoice.retail_shoe_product_ids)
                                                   )
                                                  ]

                if not result_records_na.empty:

                    pricing_tier_obj = PricingTierTable.objects \
                        .filter(product_id__product_id__in=product_ids)
                    pricing_tier_records = pd.DataFrame.from_records(pricing_tier_obj.values('product_id',
                                                                                             'tier',
                                                                                             'price',
                                                                                             'center_type'
                                                                                             ))
                    pricing_tier_records.drop_duplicates(['product_id', 'tier', 'center_type'], inplace=True)
                    pricing_tier_records.rename({'tier': 'bowling_tier', 'price': 'price_tier'}, axis=1, inplace=True)
                    pricing_tier_records['bowling_tier'] = pricing_tier_records['bowling_tier'] \
                        .apply(lambda x: str(float(x)))

                    result_records_na.loc[result_records_na['center_type'] == 'session', 'center_type'] = 'traditional'
                    result_records_na = result_records_na \
                        .join(pricing_tier_records.set_index(['product_id', 'bowling_tier', 'center_type']),
                              on=['product_id', 'bowling_tier', 'center_type'], how='left')

                    result_records = result_records.join(result_records_na[['price_tier']], how='left')
                    result_records['price'].fillna(result_records['price_tier'], inplace=True)

                result_records.dropna(subset=['price'], inplace=True)

            return result_records


class GetWeather:

    @classmethod
    def get_weather_history(cls, start, end, data_types,
                            pagination=False, page_size=None, offset=None, filters=None, sort=None, order=None):

        if sort and order:
            if order == 'desc':
                sort = '-'+sort
        else:
            sort = 'center_id'

        centers = Centers.objects \
            .filter(status='open') \
            .extra(select={'center_id': 'CAST(center_id AS INTEGER)'}) \
            .order_by(sort)

        if filters:
            filters = ast.literal_eval(filters)

            for key, value in filters.items():
                filters[key] = value.split(',')
            if filters.get('center_id'):
                filter_item = filters.get('center_id')
                if len(filter_item) == 1:
                    centers = centers.filter(center_id__icontains=filter_item[0])
                else:
                    centers = centers.filter(center_id__in=filter_item)
            if filters.get('center_name'):
                filter_item = filters.get('center_name')
                if len(filter_item) == 1:
                    centers = centers.filter(center_name__icontains=filter_item[0])
                else:
                    centers = centers.filter(center_name__in=filter_item)

        num = centers.count()

        if pagination:
            paginator = Paginator(centers, page_size, )
            current_page = int(offset / page_size) + 1
            centers = paginator.page(current_page).object_list

        centers_record = pd.DataFrame.from_records(centers
                                                   .values('center_id',
                                                           'center_name',
                                                           'weather_point_id',
                                                           ))

        if centers_record.empty:
            return pd.DataFrame(), 0
        centers_record.rename({'weather_point_id': 'point_id'}, axis=1, inplace=True)

        points_list = centers_record['point_id'].tolist()
        points_list = [point for point in points_list if point is not None]

        # Get weather info
        # Get from restored data
        weather_obj = Weather.objects \
            .filter(point_id__point_id__in=points_list,
                    data_type__in=data_types,
                    date__range=[start, end]
                    )

        weather_records = pd.DataFrame.from_records(weather_obj.values('point_id',
                                                                       'data_type',
                                                                       'date',
                                                                       'value'
                                                                       ))

        if not weather_records.empty:
            weather_records['point_id'] = weather_records['point_id'].astype(str)
            weather_records['date'] = weather_records['date'].apply(lambda x: x.date())
            weather_records = weather_records[weather_records['value'] > -100]

        # Fill none from ASCI api
        if not weather_records.empty:
            found_points = weather_records['point_id'].unique().tolist()
            record_num = len(UDatetime.date_range(start, end)) * len(data_types)
            weather_records_group = weather_records.groupby(['point_id']).count()
            partial_empty_points = weather_records_group.loc[weather_records_group['value'] < record_num].index.tolist()

            # found_points = [point for point in found_points if point not in partial_empty_points]
            found_points = [point for point in found_points]
            empty_points = [point for point in points_list if point not in found_points]
        else:
            empty_points = points_list

        if empty_points:
            empty_point_objs = Point.objects.filter(point_id__in=empty_points)
            empty_point_records = pd.DataFrame.from_records(empty_point_objs.values('point_id',
                                                                                    'longitude',
                                                                                    'latitude'
                                                                                    ))

            api_records = pd.DataFrame()
            elems_list = AcisAPI.check_elems_name(data_types)
            elems = ','.join(elems_list)
            for index, row in empty_point_records.iterrows():
                loc = AcisAPI.get_location(row['longitude'], row['latitude'])
                api_record = AcisAPI.get_weather_grid(start, end, elems, loc, grid=1)
                api_record['point_id'] = row['point_id']
                api_records = api_records.append(api_record, ignore_index=True)

            api_records = pd.melt(api_records, id_vars=['date', 'point_id'], var_name='data_type')
            api_records['value'] = pd.to_numeric(api_records['value'], errors='coerce')
            api_records['point_id'] = api_records['point_id'].astype(str)

            weather_records = api_records.append(weather_records, ignore_index=True)
            weather_records.drop_duplicates(['point_id', 'date', 'data_type'], keep='last', inplace=True)

        # Manipulate the data
        weather_records['table_field'] = weather_records[['date', 'data_type']] \
            .apply(lambda x: '{date} {data_type}'.format(date=x['date'], data_type=x['data_type']), axis=1)
        weather_records.loc[weather_records['value'] <= -100, 'value'] = None

        weather_records = pd.pivot_table(weather_records,
                                         index=['point_id'],
                                         columns=['table_field'],
                                         values=['value'],
                                         aggfunc='first'
                                         )

        weather_records.columns = weather_records.columns.droplevel(0)
        weather_records.columns.name = None
        weather_records.reset_index(inplace=True)
        if not weather_records.empty:
            centers_record = centers_record.join(weather_records.set_index(['point_id']),
                                                 on=['point_id'], how='left')

        return centers_record, num


class AlcoholGet:
    @classmethod
    def get_alcohol(cls, date, price_type, pagination=False, page_size=None, offset=None, filters=None, sort=None,
                    order=None):

        if sort and order:
            if order == 'desc':
                sort = '-' + sort
        else:
            sort = 'product_id'

        alcohol_objs = Alcohol.objects \
            .filter(product_id__status='active'
                    ) \
            .exclude(
                Q(start__gt=date) |
                Q(end__lt=date)
            ) \
            .order_by(sort)

        if filters:
            filters = ast.literal_eval(filters)

            if filters.get('product_id'):
                alcohol_objs = alcohol_objs.filter(product_id__product_id__contains=filters['product_id'])
            if filters.get('product_name'):
                alcohol_objs = alcohol_objs.filter(product_id__product_name__contains=filters['product_name'])
            if filters.get('category'):
                alcohol_objs = alcohol_objs.filter(category_id__category__contains=filters['category'])
            if filters.get('level'):
                alcohol_objs = alcohol_objs.filter(category_id__level__contains=filters['level'])
            if filters.get('traditional_menu'):
                traditional_menu_filter = filters.get('traditional_menu')
                if traditional_menu_filter == 'Yes':
                    traditional_menu_filter = True
                    alcohol_objs = alcohol_objs.filter(traditional_menu=traditional_menu_filter)
                elif traditional_menu_filter == 'No':
                    traditional_menu_filter = False
                    alcohol_objs = alcohol_objs.filter(traditional_menu=traditional_menu_filter)
            if filters.get('premium_menu'):
                premium_menu_filter = filters.get('premium_menu')
                if premium_menu_filter == 'Yes':
                    premium_menu_filter = True
                    alcohol_objs = alcohol_objs.filter(premium_menu=premium_menu_filter)
                elif premium_menu_filter == 'No':
                    premium_menu_filter = False
                    alcohol_objs = alcohol_objs.filter(premium_menu=premium_menu_filter)

        num = alcohol_objs.count()

        if pagination:
            paginator = Paginator(alcohol_objs, page_size,)
            current_page = int(offset/page_size) + 1
            alcohol_objs = paginator.page(current_page).object_list

        alcohol_record = pd.DataFrame.from_records(alcohol_objs.values(
            'product_id',
            'product_id__product_name',
            'category_id',
            'category',
            'level',
            'traditional_menu',
            'premium_menu',
            'start',
            'end',
            'action_time'
        ))
        #
        alcohol_record.rename({
            'product_id__product_name': 'product_name',
        }, axis=1, inplace=True)

        if alcohol_record.empty:
            return pd.DataFrame(), 0
        alcohol_record = alcohol_record.where((pd.notna(alcohol_record)), None)

        category_id_list = alcohol_record['category_id'].tolist()
        category_id_list = list(set([str(int(category_id)) for category_id in category_id_list if category_id]))
        tier_objs = AlcoholTier.objects \
            .filter(category_id__in=category_id_list,
                    price_type=price_type
                    )
        tier_records = pd.DataFrame.from_records(tier_objs.values(
            'category_id',
            'tier',
            'price',
            'start',
            'end',
            'action_time'
        ))

        if not tier_records.empty:
            tier_records['price'] = tier_records['price'].apply(
                lambda x: '${price}'.format(price=x))
            tier_records = pd.pivot_table(tier_records,
                                          index=['category_id'],
                                          columns=['tier'],
                                          values=['price'],
                                          aggfunc='first'
                                         )
            tier_records.columns = tier_records.columns.droplevel(0)
            tier_records.columns.name = None
            tier_records.reset_index(inplace=True)

            alcohol_record = alcohol_record \
                .join(tier_records.set_index(['category_id']),
                      on=['category_id'], how='left')

        if alcohol_record.empty:
            return pd.DataFrame(), 0

        return alcohol_record, num

    @classmethod
    def get_alcoholtier(cls, date, price_type, categories=None, tiers=None, add_dollar_symbol=True,
                        pagination=False, page_size=None, offset=None, filters=None, sort=None, order=None):

        if sort and order:
            if order == 'desc':
                sort = '-' + sort
        else:
            sort = 'category_id'

        category_objs = AlcoholCategory.objects \
            .filter() \
            .order_by(sort)

        if categories:
            category_objs = category_objs.filter(category_id__in=categories)

        if filters:
            filters = ast.literal_eval(filters)

            if filters.get('category'):
                category_objs = category_objs.filter(category__contains=filters['category'])
            if filters.get('level'):
                category_objs = category_objs.filter(category_id__level=filters['level'])

        num = category_objs.count()

        if pagination:
            paginator = Paginator(category_objs, page_size,)
            current_page = int(offset/page_size) + 1
            category_objs = paginator.page(current_page).object_list

        category_record = pd.DataFrame.from_records(category_objs.values(
            'category_id',
            'category',
            'level',
            'action_time'
        ))

        category_record.rename({
        }, axis=1, inplace=True)

        if category_record.empty:
            return pd.DataFrame(), 0

        category_id_list = category_record['category_id'].tolist()

        tier_objs = AlcoholTier.objects \
            .filter(category_id__in=category_id_list,
                    price_type=price_type
                    ) \
            .exclude(
                Q(start__gt=date) |
                Q(end__lt=date)
            )

        if tiers:
            tier_objs = tier_objs.filter(tier__in=tiers)

        tier_records = pd.DataFrame.from_records(tier_objs.values(
            'category_id',
            'tier',
            'price',
            'start',
            'end',
            'action_time'
        ))

        if not tier_records.empty:
            tier_records['price'] = tier_records['price'].apply(lambda x: round(x, 2))
            if add_dollar_symbol:
                tier_records['price'] = tier_records['price'].apply(
                    lambda x: '${price}'.format(price=x))
            tier_records = pd.pivot_table(tier_records,
                                          index=['category_id'],
                                          columns=['tier'],
                                          values=['price'],
                                          aggfunc='first'
                                         )
            tier_records.columns = tier_records.columns.droplevel(0)
            tier_records.columns.name = None
            tier_records.reset_index(inplace=True)

            category_record = category_record \
                .join(tier_records.set_index(['category_id']),
                      on=['category_id'], how='left')

        if category_record.empty:
            return pd.DataFrame(), 0

        return category_record, num


class BundleGet:
    @classmethod
    def get_bundle(cls, pagination=False, page_size=None, offset=None, filters=None, sort=None,
                   order=None):

        if sort and order:
            if order == 'desc':
                sort = '-' + sort
        else:
            sort = 'bundle_id'

        bundle_objs = Bundle.objects \
            .filter() \
            .order_by(sort)

        if filters:
            filters = ast.literal_eval(filters)

            if filters.get('bundle_name'):
                bundle_objs = bundle_objs.filter(bundle_name__contains=filters['bundle_name'])
            if filters.get('products'):
                bundle_objs = bundle_objs.filter(bundleproduct__product_id__product_name__contains=filters['products'])

        num = bundle_objs.count()

        if pagination:
            paginator = Paginator(bundle_objs, page_size,)
            current_page = int(offset/page_size) + 1
            bundle_objs = paginator.page(current_page).object_list

        bundle_record = pd.DataFrame.from_records(bundle_objs.values(
            'bundle_id',
            'bundle_name',
        ))
        #
        bundle_record.rename({
        }, axis=1, inplace=True)

        if bundle_record.empty:
            return pd.DataFrame(), 0

        bundle_id_list = bundle_objs.values_list('bundle_id', flat=True)

        bundleproduct_obj = BundleProduct.objects.filter(bundle_id__in=bundle_id_list)
        bundleproduct_records = pd.DataFrame.from_records(bundleproduct_obj.values(
            'bundle_id',
            'product_id__product_name',
        ))
        bundleproduct_records.rename({
            'product_id__product_name': 'product_name'
        }, axis=1, inplace=True)

        bundleproduct_records_grp = bundleproduct_records.groupby(['bundle_id'])\
            .apply(lambda x: ','.join(x['product_name']))
        bundleproduct_records_grp.rename('products', inplace=True)
        bundle_record = bundle_record.join(bundleproduct_records_grp, on=['bundle_id'], how='left')

        return bundle_record, num

    @classmethod
    def get_bundle_detail(cls, bundle_id, pagination=False, page_size=None, offset=None, filters=None, sort=None,
                          order=None):

        if sort and order:
            if order == 'desc':
                sort = '-' + sort
        else:
            sort = 'bundle_id'

        bundleproduct_objs = BundleProduct.objects \
            .filter(bundle_id=bundle_id) \
            .order_by(sort)

        if filters:
            filters = ast.literal_eval(filters)
            if filters.get('product_num'):
                bundleproduct_objs = bundleproduct_objs.filter(product_id__product_num__contains=filters['product_num'])
            if filters.get('product_name'):
                bundleproduct_objs = bundleproduct_objs.filter(product_id__product_name__contains=filters['product_name'])

        num = bundleproduct_objs.count()

        if pagination:
            paginator = Paginator(bundleproduct_objs, page_size,)
            current_page = int(offset/page_size) + 1
            bundle_objs = paginator.page(current_page).object_list

        bundleproduct_record = pd.DataFrame.from_records(bundleproduct_objs.values(
            'product_id__product_num',
            'product_id__product_name',
        ))
        #
        bundleproduct_record.rename({
            'product_id__product_num': 'product_num',
            'product_id__product_name': 'product_name'
        }, axis=1, inplace=True)

        if bundleproduct_record.empty:
            return pd.DataFrame(), 0

        return bundleproduct_record, num


class GetEvent:
    @classmethod
    def get_event_price_tier(cls, group, subGroup, tier,
                             pagination=False, page_size=None, offset=None, filters=None, sort=None, order=None):
        # Back
        SpecialProds = ['Lane', 'Unlimited Arcade']
        # SpecialProds = []

        if sort and order:
            if order == 'desc':
                sort = '-'+sort
        else:
            sort = 'tier'

        if group in SpecialProds:
            tier_objs = EventTier.objects.filter(group=group, tier=tier)
            tier_objs = tier_objs.order_by('subGroup')

            tier_record = pd.DataFrame.from_records(tier_objs.values(
                'product',
                'subGroup',
                'price',
            ))
            tier_record = tier_record.where((pd.notnull(tier_record)), None)

            if not tier_record.empty:
                tier_record['price'] = tier_record['price'].apply(lambda x: str(int(x)) if x and x % 1 == 0 else x)
                tier_record['price'] = tier_record['price'].apply(lambda x: '${price}'.format(price=x) if x else None)
                tier_record = pd.pivot_table(tier_record,
                                             index=['subGroup'],
                                             columns=['product'],
                                             values=['price'],
                                             aggfunc='first'
                                             )
                tier_record.columns = tier_record.columns.droplevel(0)
                tier_record.columns.name = None
                tier_record.reset_index(inplace=True)

                if sort and order:
                    if order == 'desc':
                        order = False
                        sort = sort.replace('-', '')
                    else:
                        order = True
                tier_record.sort_values(by=['subGroup'], ascending=[order], inplace=True)
                tier_record = tier_record.apply(np.roll, shift=1)
            else:
                tier_record = pd.DataFrame()

            # Back
            # Fill None Columns
            columns = EventTier.objects.filter(group=group).values_list('product', flat=True).distinct()
            for column in columns:
                if column not in tier_record.columns:
                    tier_record[column] = np.nan

            num = len(tier_record)

            return tier_record, num
        else:
            tier_objs = EventTier.objects.filter(group=group, subGroup=subGroup)
            if tier and tier != 'All':
                tier_objs = tier_objs.filter(tier=tier)
            tier_objs = tier_objs.order_by(sort)

            if filters:
                filters = ast.literal_eval(filters)

                for key, value in filters.items():
                    filters_list = value.split(',')
                    filters_list = [x.strip() for x in filters_list]
                    filters[key] = filters_list
                if filters.get('tier'):
                    filter_item = filters.get('tier')
                    if len(filter_item) == 1:
                        tier_objs = tier_objs.filter(tier__icontains=filter_item[0])
                    else:
                        tier_objs = tier_objs.filter(tier__in=filter_item)

            # num = pricing_tier.count()

            # if pagination:
            #     paginator = Paginator(pricing_tier, page_size,)
            #     current_page = int(offset/page_size) + 1
            #     pricing_tier = paginator.page(current_page).object_list

            tier_record = pd.DataFrame.from_records(tier_objs.values(
                    'product',
                    'tier',
                    'price',
                ))
            tier_record = tier_record.where((pd.notnull(tier_record)), None)

            if not tier_record.empty:
                tier_record['price'] = tier_record['price'].apply(lambda x: str(int(x)) if x and x % 1 == 0 else x)
                tier_record['price'] = tier_record['price'].apply(lambda x: '${price}'.format(price=x) if x else None)
                tier_record = pd.pivot_table(tier_record,
                                             index=['tier'],
                                             columns=['product'],
                                             values=['price'],
                                             aggfunc='first'
                                             )
                tier_record.columns = tier_record.columns.droplevel(0)
                tier_record.columns.name = None
                tier_record.reset_index(inplace=True)
                tier_record['tier'] = tier_record['tier'].astype(float)

                if sort and order:
                    if order == 'desc':
                        order = False
                        sort = sort.replace('-', '')
                    else:
                        order = True
                tier_record.sort_values(by=[sort], ascending=[order], inplace=True)
            else:
                return pd.DataFrame(), 0

            num = len(tier_record)

            return tier_record, num

    @classmethod
    def get_event_allocation(cls, group, subGroup, product, tier,
                             pagination=False, page_size=None, offset=None, filters=None, sort=None, order=None):

        if sort and order:
            if order == 'desc':
                sort = '-'+sort
        else:
            sort = 'tier'

        allc_objs = EventAllocation.objects.filter(group=group, subGroup=subGroup)
        if tier and tier != 'All':
            allc_objs = allc_objs.filter(tier=tier)

        allc_objs = allc_objs \
            .filter(product=product) \
            .order_by(sort)

        if filters:
            filters = ast.literal_eval(filters)

            for key, value in filters.items():
                filters_list = value.split(',')
                filters_list = [x.strip() for x in filters_list]
                filters[key] = filters_list
            if filters.get('tier'):
                filter_item = filters.get('tier')
                if len(filter_item) == 1:
                    allc_objs = allc_objs.filter(tier__icontains=filter_item[0])
                else:
                    allc_objs = allc_objs.filter(tier__in=filter_item)

        # num = pricing_tier.count()

        # if pagination:
        #     paginator = Paginator(pricing_tier, page_size,)
        #     current_page = int(offset/page_size) + 1
        #     pricing_tier = paginator.page(current_page).object_list

        allc_record = pd.DataFrame.from_records(allc_objs.values(
                'subProduct',
                'tier',
                'price'
            ))

        if not allc_record.empty:
            allc_record['price'] = allc_record['price'].apply(lambda x: str(int(x)) if x and x % 1 == 0 else x)
            allc_record['price'] = allc_record['price'].apply(lambda x: '${price}'.format(price=x))
            allc_record = pd.pivot_table(allc_record,
                                         index=['tier'],
                                         columns=['subProduct'],
                                         values=['price'],
                                         aggfunc='first'
                                         )
            allc_record.columns = allc_record.columns.droplevel(0)
            allc_record.columns.name = None
            allc_record.reset_index(inplace=True)
            allc_record['tier'] = allc_record['tier'].astype(float)

            if sort and order:
                if order == 'desc':
                    order = False
                    sort = sort.replace('-', '')
                else:
                    order = True
            allc_record.sort_values(by=[sort], ascending=[order], inplace=True)
        else:
            return pd.DataFrame(), 0

        num = len(allc_record)

        return allc_record, num

    @classmethod
    def get_event_price_by_center(cls, groupSelections, productSelections, centerSelections,
                                  pagination=False, page_size=None, offset=None, filters=None, sort=None, order=None):

        if sort and order:
            if order == 'desc':
                sort = '-'+sort
        else:
            sort = 'order'

        product_objs = EventPriceByCenter.objects \
            .filter() \
            .order_by(sort)

        # filter by selections first
        if 'All' not in groupSelections and groupSelections:
            product_objs = product_objs.filter(group__in=groupSelections)
        if 'All' not in productSelections and productSelections:
            product_objs = product_objs.filter(product__in=productSelections)
        if 'All' not in centerSelections and centerSelections:
            product_objs = product_objs.filter(center_id__center_id__in=centerSelections)

        if filters:
            filters = ast.literal_eval(filters)

            for key, value in filters.items():
                filters_list = value.split(',')
                filters_list = [x.strip() for x in filters_list]
                filters[key] = filters_list
            if filters.get('center_id'):
                filter_item = filters.get('center_id')
                if len(filter_item) == 1:
                    product_objs = product_objs.filter(center_id__center_id__icontains=filter_item[0])
                else:
                    product_objs = product_objs.filter(center_id__center_id__in=filter_item)
            if filters.get('center_name'):
                filter_item = filters.get('center_name')
                if len(filter_item) == 1:
                    product_objs = product_objs.filter(center_id__center_name__icontains=filter_item[0])
                else:
                    product_objs = product_objs.filter(reduce(operator.or_, (Q(center_id__center_name__icontains=item)
                                                                             for item in filter_item if item)))
            if filters.get('sale_region'):
                filter_item = filters.get('sale_region')
                if len(filter_item) == 1:
                    product_objs = product_objs.filter(center_id__sale_region__icontains=filter_item[0])
                else:
                    product_objs = product_objs.filter(reduce(operator.or_, (Q(center_id__sale_region__icontains=item)
                                                                             for item in filter_item if item)))
            if filters.get('territory'):
                filter_item = filters.get('territory')
                if len(filter_item) == 1:
                    product_objs = product_objs.filter(center_id__territory__icontains=filter_item[0])
                else:
                    product_objs = product_objs.filter(reduce(operator.or_, (Q(center_id__territory__icontains=item)
                                                                             for item in filter_item if item)))
            if filters.get('group'):
                filter_item = filters.get('group')
                if len(filter_item) == 1:
                    product_objs = product_objs.filter(group__icontains=filter_item[0])
                else:
                    product_objs = product_objs.filter(reduce(operator.or_, (Q(group__icontains=item)
                                                                             for item in filter_item if item)))
            if filters.get('product'):
                filter_item = filters.get('product')
                if len(filter_item) == 1:
                    product_objs = product_objs.filter(product__icontains=filter_item[0])
                else:
                    product_objs = product_objs.filter(reduce(operator.or_, (Q(product__icontains=item)
                                                                             for item in filter_item if item)))

        product_records = pd.DataFrame.from_records(product_objs.values(
            'center_id',
            'center_id__center_name',
            'center_id__sale_region',
            'center_id__territory',
            'group',
            'product',
            'duration',
            'price',
            'order',
        ))
        product_records = product_records.where((pd.notnull(product_records)), None)

        if not product_records.empty:
            product_records.rename({'center_id__center_name': 'center_name',
                                    'center_id__sale_region': 'sale_region',
                                    'center_id__territory': 'territory'
                                    }, axis=1, inplace=True)
            # product_records['price'] = product_records['price'].apply(lambda x: '${price}'.format(price=x))
            # Back
            product_records['price'] = product_records['price'].apply(lambda x: str(int(x)) if x and x % 1 == 0 else x)
            product_records['price'] = product_records['price']\
                .apply(lambda x: '${price}'.format(price=x) if x else None)
            product_records = pd.pivot_table(product_records,
                                             index=['center_id', 'center_name', 'sale_region',
                                                    'territory', 'group', 'product', 'order'],
                                             columns=['duration'],
                                             values=['price'],
                                             aggfunc='first'
                                             )
            product_records.columns = product_records.columns.droplevel(0)
            product_records.columns.name = None
            product_records.reset_index(inplace=True)
            product_records['center_id'] = product_records['center_id'].astype(int)
            # Back
            product_records.sort_values(by=['center_id', sort], inplace=True)

            # Back
            # Fill None Columns
            columns = EventPriceByCenter.objects.filter().values_list('duration', flat=True).distinct()
            for column in columns:
                if column not in product_records.columns:
                    product_records[column] = np.nan
        else:
            return pd.DataFrame(), 0

        num = len(product_records)

        if pagination:
            product_records = product_records[int(offset): int(offset + page_size)]

        return product_records, num

    @classmethod
    def get_event_price_table(cls, start, end, product,
                              pagination=False, page_size=None, offset=None, filters=None, sort=None, order=None):

        # init
        date_range = UDatetime.date_range(start, end)

        center_name_replace = {
            'AMF': '',
            'Bowlero': '',
            'Bowlmor': '',
            'Brunswick Zone': ''
        }

        result_record = pd.DataFrame()

        # find centers
        if sort and order:
            if order == 'desc':
                sort = '-'+sort
        else:
            sort = 'center_id'

        centers = Centers.objects\
            .filter(status='open') \
            .extra(select={'center_id': 'CAST(center_id AS INTEGER)'}) \
            .order_by(sort)

        if filters:
            filters = ast.literal_eval(filters)

            if filters.get('center_id'):
                centers = centers.filter(center_id__contains=filters['center_id'])
            if filters.get('center_name'):
                centers = centers.filter(center_name__contains=filters['center_name'])
            if filters.get('brand'):
                centers = centers.filter(brand__contains=filters['brand'])
            if filters.get('region'):
                centers = centers.filter(region__contains=filters['region'])
            if filters.get('district'):
                centers = centers.filter(district__contains=filters['district'])
            if filters.get('status'):
                centers = centers.filter(status__exact=filters['status'])
            if filters.get('time_zone'):
                centers = centers.filter(time_zone__exact=filters['time_zone'])
            if filters.get('bowling_tier'):
                centers = centers.filter(bowling_tier__contains=filters['bowling_tier'])
            if filters.get('food_tier'):
                centers = centers.filter(food_tier__contains=filters['food_tier'])
            if filters.get('food_menu'):
                centers = centers.filter(food_menu__contains=filters['food_menu'])

        num = centers.count()

        if pagination:
            paginator = Paginator(centers, page_size,)
            current_page = int(offset/page_size) + 1
            centers = paginator.page(current_page).object_list

        centers_id_list = centers.values_list('center_id', flat=True)
        centers_id_list = [str(x) for x in centers_id_list]
        if not centers_id_list:
            return result_record, num

        # init result records
        result_list = [
            {'center_id': center_id,
             'product_id': product_id
             }
            for center_id in centers_id_list for product_id in product
        ]
        result_record = pd.DataFrame(result_list)

        # Center
        centers_records = pd.DataFrame.from_records(centers.values('center_id',
                                                                   'center_name',
                                                                   'district',
                                                                   'region',
                                                                   'brand',
                                                                   'bowling_event_tier',
                                                                   'food_tier',
                                                                   'food_menu',
                                                                   'center_type'
                                                                   ))
        centers_records['center_id'] = centers_records['center_id'].astype('str')
        result_record = result_record.join(centers_records.set_index(['center_id']),
                                           on=['center_id'], how='left')

        # Product
        product_obj = Product.objects.filter(product_id__in=product)
        if product_obj.exists():
            product_records = pd.DataFrame.from_records(product_obj.values('product_id', 'short_product_name'))
            product_records.rename({'short_product_name': 'product_name'}, axis=1, inplace=True)
            result_record = result_record.join(product_records.set_index(['product_id']),
                                               on=['product_id'], how='left')
        else:
            result_record['product_name'] = None

        # Product Opt
        # product_opt = ProductOptGet.get_productopt(product, start, end, centers_id_list)
        # product_opt_one = product_opt.drop_duplicates(['center_id', 'product_id'])
        # if not product_opt.empty:
        #     result_record = result_record.join(product_opt_one.set_index(['center_id', 'product_id']),
        #                                        on=['center_id', 'product_id'], how='left')
        # else:
        #     result_record['opt'] = None
        # result_record = result_record.where((pd.notnull(result_record)), '')

        # Product Price
        price_record = PriceChange.get_price_by_date_range(product, start, end, centers_id_list)
        if not price_record.empty:

            # filter out product opt out
            price_record['date'] = price_record['date'].apply(lambda x: str(x.date()))
            price_record['price'] = price_record['price'].apply(lambda x: '${price}'.format(price=x))
            # result_record = result_record.where((pd.notnull(result_record)), "")

            price_record = pd.pivot_table(price_record,
                                          index=['center_id', 'product_id'],
                                          columns=['date'],
                                          values=['price'],
                                          aggfunc='first'
                                         )

            price_record.columns = price_record.columns.droplevel(0)
            price_record.columns.name = None
            price_record.reset_index(inplace=True)

            for date in date_range:
                date = str(date)
                if date not in price_record.columns:
                    price_record[date] = np.nan

            result_record = result_record.join(price_record.set_index(['center_id', 'product_id']),
                                               on=['center_id', 'product_id'], how='left')
        else:
            for date in date_range:
                date = str(date)
                result_record[date] = np.nan

        result_record['center_name'].replace(center_name_replace, inplace=True, regex=True)
        result_record.sort_values(['center_id', 'product_id'], inplace=True)

        return result_record, num

    @classmethod
    def get_event_promo(cls, pagination=False, page_size=None, offset=None, filters=None, sort=None, order=None):

        if sort and order:
            if order == 'desc':
                sort = '-' + sort
        else:
            sort = '-promo_code'

        promo_obj = EventPromo.objects \
            .all() \
            .order_by(sort)

        if filters:
            filters = ast.literal_eval(filters)

            for key, value in filters.items():
                filters_list = value.split(',')
                filters_list = [x.strip() for x in filters_list]
                filters[key] = filters_list
            if filters.get('promo_code'):
                filter_item = filters.get('promo_code')
                if len(filter_item) == 1:
                    promo_obj = promo_obj.filter(promo_code__icontains=filter_item[0])
                else:
                    promo_obj = promo_obj.filter(reduce(operator.or_, (Q(promo_code__icontains=item)
                                                                       for item in filter_item if item)))
            if filters.get('description'):
                filter_item = filters.get('description')
                if len(filter_item) == 1:
                    promo_obj = promo_obj.filter(description__icontains=filter_item[0])
                else:
                    promo_obj = promo_obj.filter(reduce(operator.or_, (Q(description__icontains=item)
                                                                       for item in filter_item if item)))
            if filters.get('start'):
                filter_item = filters.get('start')
                if len(filter_item) == 1:
                    promo_obj = promo_obj.filter(start__icontains=filter_item[0])
                else:
                    promo_obj = promo_obj.filter(reduce(operator.or_, (Q(start__icontains=item)
                                                                       for item in filter_item if item)))
            if filters.get('end'):
                filter_item = filters.get('end')
                if len(filter_item) == 1:
                    promo_obj = promo_obj.filter(end__icontains=filter_item[0])
                else:
                    promo_obj = promo_obj.filter(reduce(operator.or_, (Q(end__icontains=item)
                                                                       for item in filter_item if item)))
            if filters.get('eventByDate'):
                filter_item = filters.get('eventByDate')
                if len(filter_item) == 1:
                    promo_obj = promo_obj.filter(eventByDate__icontains=filter_item[0])
                else:
                    promo_obj = promo_obj.filter(reduce(operator.or_, (Q(eventByDate__icontains=item)
                                                                       for item in filter_item if item)))
            if filters.get('comment'):
                filter_item = filters.get('comment')
                if len(filter_item) == 1:
                    promo_obj = promo_obj.filter(comment__icontains=filter_item[0])
                else:
                    promo_obj = promo_obj.filter(reduce(operator.or_, (Q(comment__icontains=item)
                                                                       for item in filter_item if item)))

        num = promo_obj.count()

        if pagination:
            paginator = Paginator(promo_obj, page_size, )
            current_page = int(offset / page_size) + 1
            promo_obj = paginator.page(current_page).object_list

        promo_record = pd.DataFrame.from_records(promo_obj.values(
            'id',
            'promo_code',
            'description',
            'start',
            'end',
            'eventByDate',
            'comment'
        ))

        if promo_record.empty:
            return pd.DataFrame(), 0

        return promo_record, num

    @classmethod
    def get_event_overview(cls, pagination=False, page_size=None, offset=None, filters=None, sort=None, order=None):

        if sort and order:
            if order == 'desc':
                sort = '-'+sort
        else:
            sort = 'center_id'

        centers = Centers.objects \
            .filter(status='open') \
            .extra(select={'center_id': 'CAST(center_id AS INTEGER)'}) \
            .order_by(sort)

        productopt_records = pd.DataFrame()

        if filters:
            filters = ast.literal_eval(filters)

            for key, value in filters.items():
                filters_list = value.split(',')
                filters_list = [x.strip() for x in filters_list]
                filters[key] = filters_list
            if filters.get('center_id'):
                filter_item = filters.get('center_id')
                if len(filter_item) == 1:
                    centers = centers.filter(center_id__icontains=filter_item[0])
                else:
                    centers = centers.filter(center_id__in=filter_item)
            if filters.get('center_name'):
                filter_item = filters.get('center_name')
                if len(filter_item) == 1:
                    centers = centers.filter(center_name__icontains=filter_item[0])
                else:
                    centers = centers.filter(reduce(operator.or_, (Q(center_name__icontains=item)
                                                                   for item in filter_item if item)))
            if filters.get('status'):
                filter_item = filters.get('status')
                if len(filter_item) == 1:
                    centers = centers.filter(status__exact=filter_item[0])
                else:
                    centers = centers.filter(status__in=filter_item)
            if filters.get('sale_region'):
                filter_item = filters.get('sale_region')
                if len(filter_item) == 1:
                    centers = centers.filter(sale_region__icontains=filter_item[0])
                else:
                    centers = centers.filter(reduce(operator.or_, (Q(sale_region__icontains=item)
                                                                   for item in filter_item if item)))
            if filters.get('territory'):
                filter_item = filters.get('territory')
                if len(filter_item) == 1:
                    centers = centers.filter(territory__icontains=filter_item[0])
                else:
                    centers = centers.filter(reduce(operator.or_, (Q(territory__icontains=item)
                                                                   for item in filter_item if item)))
            if filters.get('arcade_type'):
                filter_item = filters.get('arcade_type')
                if len(filter_item) == 1:
                    centers = centers.filter(arcade_type__icontains=filter_item[0])
                else:
                    centers = centers.filter(reduce(operator.or_, (Q(arcade_type__icontains=item)
                                                                   for item in filter_item if item)))
            if filters.get('center_type'):
                filter_item = filters.get('center_type')
                if len(filter_item) == 1:
                    centers = centers.filter(center_type__icontains=filter_item[0])
                else:
                    centers = centers.filter(reduce(operator.or_, (Q(center_type__icontains=item)
                                                                   for item in filter_item if item)))

        num = centers.count()

        if pagination:
            paginator = Paginator(centers, page_size,)
            current_page = int(offset/page_size) + 1
            centers = paginator.page(current_page).object_list

        centers_record = pd.DataFrame.from_records(centers
                                                   .values('center_id',
                                                           'center_name',
                                                           'status',
                                                           'sale_region',
                                                           'territory',
                                                           'arcade_type',
                                                           'center_type',
                                                           ))

        if centers_record.empty:
            return pd.DataFrame(), 0

        # add star for session center
        def session_center_star(row):
            if row['center_type'] == 'session':
                return '*{center_id}'.format(center_id=row['center_id'])
            else:
                return row['center_id']
        centers_record['center_id'] = centers_record.apply(session_center_star, axis=1)

        # capitalize string
        centers_record['center_type'] = centers_record['center_type'].str.capitalize()

        return centers_record, num

    @classmethod
    def get_center_tier(cls, pagination=False, page_size=None, offset=None, filters=None, sort=None, order=None):

        if sort and order:
            if order == 'desc':
                sort = '-'+sort
        else:
            sort = 'center_id'

        centers = Centers.objects \
            .filter(status='open') \
            .extra(select={'center_id': 'CAST(center_id AS INTEGER)'}) \
            .order_by(sort)

        if filters:
            filters = ast.literal_eval(filters)

            for key, value in filters.items():
                filters_list = value.split(',')
                filters_list = [x.strip() for x in filters_list]
                filters[key] = filters_list
            if filters.get('center_id'):
                filter_item = filters.get('center_id')
                if len(filter_item) == 1:
                    centers = centers.filter(center_id__icontains=filter_item[0])
                else:
                    centers = centers.filter(center_id__in=filter_item)
            if filters.get('center_name'):
                filter_item = filters.get('center_name')
                if len(filter_item) == 1:
                    centers = centers.filter(center_name__icontains=filter_item[0])
                else:
                    centers = centers.filter(reduce(operator.or_, (Q(center_name__icontains=item)
                                                                   for item in filter_item if item)))
            if filters.get('status'):
                filter_item = filters.get('status')
                if len(filter_item) == 1:
                    centers = centers.filter(status__exact=filter_item[0])
                else:
                    centers = centers.filter(status__in=filter_item)
            if filters.get('sale_region'):
                filter_item = filters.get('sale_region')
                if len(filter_item) == 1:
                    centers = centers.filter(sale_region__icontains=filter_item[0])
                else:
                    centers = centers.filter(reduce(operator.or_, (Q(sale_region__icontains=item)
                                                                   for item in filter_item if item)))
            if filters.get('territory'):
                filter_item = filters.get('territory')
                if len(filter_item) == 1:
                    centers = centers.filter(territory__icontains=filter_item[0])
                else:
                    centers = centers.filter(reduce(operator.or_, (Q(territory__icontains=item)
                                                                   for item in filter_item if item)))
            if filters.get('center_type'):
                filter_item = filters.get('center_type')
                if len(filter_item) == 1:
                    centers = centers.filter(center_type__icontains=filter_item[0])
                else:
                    centers = centers.filter(reduce(operator.or_, (Q(center_type__icontains=item)
                                                                   for item in filter_item if item)))
            if filters.get('arcade_type'):
                filter_item = filters.get('arcade_type')
                if len(filter_item) == 1:
                    centers = centers.filter(arcade_type__icontains=filter_item[0])
                else:
                    centers = centers.filter(reduce(operator.or_, (Q(arcade_type__icontains=item)
                                                                   for item in filter_item if item)))

        num = centers.count()

        if pagination:
            paginator = Paginator(centers, page_size,)
            current_page = int(offset/page_size) + 1
            centers = paginator.page(current_page).object_list

        centers_id_list = centers.values_list('center_id', flat=True)
        centers_record = pd.DataFrame.from_records(centers
                                                   .values('center_id',
                                                           'center_name',
                                                           'status',
                                                           'sale_region',
                                                           'territory',
                                                           'center_type',
                                                           'arcade_type',
                                                           ))

        if centers_record.empty:
            return pd.DataFrame(), 0

        # Get Product tier
        center_tier_objs = EventCenterTier.objects.filter(center_id__center_id__in=centers_id_list)
        center_tier_records = pd.DataFrame.from_records(center_tier_objs.values('center_id',
                                                                                'product',
                                                                                'tier'))

        center_tier_records = pd.pivot_table(center_tier_records,
                                             index=['center_id'],
                                             columns=['product'],
                                             values=['tier'],
                                             aggfunc='first'
                                             )

        center_tier_records.columns = center_tier_records.columns.droplevel(0)
        center_tier_records.columns.name = None
        center_tier_records.reset_index(inplace=True)

        center_tier_records['center_id'] = center_tier_records['center_id'].apply(int)
        centers_record = centers_record.join(center_tier_records.set_index(['center_id']),
                                             on=['center_id'], how='left')

        # add star for session center
        def session_center_star(row):
            if row['center_type'] == 'session':
                return '*{center_id}'.format(center_id=row['center_id'])
            else:
                return row['center_id']
        centers_record['center_id'] = centers_record.apply(session_center_star, axis=1)

        # capitalize string
        centers_record['center_type'] = centers_record['center_type'].str.capitalize()

        return centers_record, num


class PriceChange:

    @classmethod
    def get_last_price(cls, product_ids, center_ids=None, as_of_date=None, perpetual_only=False):
        # Init price
        if not as_of_date:
            as_of_date = UDatetime.now_local().date()

        if not center_ids:
            center_ids = Centers.objects.filter(status='open').values_list('center_id')

        # Find last price
        price_obj = ProductPriceChange.objects \
            .filter(product_id__product_id__in=product_ids,
                    center_id__center_id__in=center_ids
                    ) \
            .exclude(Q(start__gt=as_of_date) |
                     Q(end__lt=as_of_date)
                     )

        if perpetual_only:
            price_obj = price_obj.filter(perpetual=True)

        price_records = pd.DataFrame.from_records(price_obj.values('center_id',
                                                                   'product_id',
                                                                   'price',
                                                                   'action_time',
                                                                   ))

        if price_records.empty:
            return pd.DataFrame()

        price_records = price_records \
            .sort_values(['center_id', 'product_id', 'action_time']) \
            .drop_duplicates(['center_id', 'product_id'], keep='last')

        return price_records

    @classmethod
    def get_price_by_date_range(cls, product_ids, start=None, end=None, center_ids=None):
        if not start:
            start = UDatetime.now_local().date()
        if not end:
            end = UDatetime.now_local().date()

        if not center_ids:
            center_ids = Centers.objects.filter(status='open').values_list('center_id')

        # Find last price
        price_obj = ProductPriceChange.objects \
            .filter(product_id__product_id__in=product_ids,
                    center_id__center_id__in=center_ids
                    ) \
            .exclude(Q(start__gt=end) |
                     Q(end__lt=start)
                     )

        price_records = pd.DataFrame.from_records(price_obj.values('center_id',
                                                                   'product_id',
                                                                   'price',
                                                                   'start',
                                                                   'end',
                                                                   'action_time',
                                                                   ))

        if price_records.empty:
            return pd.DataFrame()

        price_records.sort_values(['action_time'], ascending=[False], inplace=True)
        # init to_records
        to_date_range = UDatetime.date_range(start, end)

        if not to_date_range:
            return pd.DataFrame()
        to_records_list = [
            {'center_id': center_id, 'product_id': product_id, 'date': date,
             'DOW': DOW_choice[date.weekday()][0]}
            for center_id in center_ids
            for product_id in product_ids
            for date in to_date_range
        ]
        to_records = pd.DataFrame(to_records_list)

        # get product schedule
        productschedule_obj = ProductSchedule.objects.filter(product_id__product_id__in=product_ids,
                                                             status='active')
        productschedule_records = pd.DataFrame.from_records(productschedule_obj.values('product_id__product_id',
                                                                                       'DOW'))
        if productschedule_records.empty:
            return pd.DataFrame()
        productschedule_records.rename({'product_id__product_id': 'product_id'}, axis=1, inplace=True)
        productschedule_records.drop_duplicates(['product_id', 'DOW'], inplace=True)
        productschedule_records['available'] = True

        to_records = to_records.join(productschedule_records.set_index(['product_id', 'DOW']),
                                     on=['product_id', 'DOW'], how='left')

        # Get product opt in / out
        productopt_records = ProductOptGet.get_productopt(product_ids, start, end, center_ids)
        if productopt_records.empty:
            return pd.DataFrame()

        to_records['date'] = to_records['date'].apply(lambda x: str(x))
        productopt_records['date'] = productopt_records['date'].apply(lambda x: str(x))

        to_records = to_records.join(productopt_records.set_index(['center_id', 'product_id', 'date']),
                                     on=['center_id', 'product_id', 'date'], how='left')

        to_records = to_records[(to_records['available']) & (to_records['opt'] == 'In')]
        if to_records.empty:
            return pd.DataFrame()

        to_records.reset_index(drop=True, inplace=True)
        to_records['price'] = None
        to_records['date'] = pd.to_datetime(to_records['date'])
        for index, row in price_records.iterrows():
            start_row = row['start']
            end_row = row['end']
            if not start_row or pd.isnull(start_row):
                start_row = start
            if not end_row or pd.isnull(end_row):
                end_row = end

            is_empty = to_records[pd.isnull(to_records['price'])].empty
            if is_empty:
                break

            to_records \
                .loc[
                     (to_records['date'] >= start_row) &
                     (to_records['date'] <= end_row) &
                     (to_records['center_id'] == row['center_id']) &
                     (to_records['product_id'] == row['product_id']) &
                     (pd.isnull(to_records['price'])),
                     'price'] \
                = row['price']

        return to_records
