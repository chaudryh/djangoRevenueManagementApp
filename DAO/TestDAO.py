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


class TestDAO:

    @classmethod
    def get_centers(cls, region, district, columns, pagination=False, page_size=None, offset=None, filters=None, sort=None, order=None):

        if sort and order:
            if order == 'desc':
                sort = '-'+sort
        else:
            sort = 'center_id'

        centers = Centers.objects\
            .filter(status='open',) \
            .extra(select={'center_id': 'CAST(center_id AS INTEGER)'})\
            .order_by(sort)

        if region and district:
            centers = centers.filter(region__in=region, district__in=district)
        elif region:
            centers = centers.filter(region__in=region,)
        elif district:
            centers = centers.filter(district__in=district)

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
            #These filter are no longer being used
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
                                                           'region',
                                                           'district',
                                                           ))

        if columns:
            centers_record = centers_record[columns]

        # centers_record.rename({'center_id': 'ID',
        #                                'center_name': 'Center Name'},
        #                       axis='columns', inplace=True
        #                       )

        if centers_record.empty:
            return pd.DataFrame(), 0

        return centers_record, num

class GetEvent:
    @classmethod
    def get_event_overview(cls, sale_region, territory, pagination=False, page_size=None, offset=None, filters=None, sort=None, order=None):
        #print(sale_region, territory)

        if sort and order:
            if order == 'desc':
                sort = '-' + sort
        else:
            sort = 'center_id'

        centers = Centers.objects \
            .filter(status='open') \
            .extra(select={'center_id': 'CAST(center_id AS INTEGER)'}) \
            .order_by(sort)

        if sale_region and territory:
            centers = centers.filter(sale_region__in=sale_region, territory__in=territory)
        elif sale_region:
            centers = centers.filter(sale_region__in=sale_region,)
        elif territory:
            centers = centers.filter(territory__in=territory)

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
            paginator = Paginator(centers, page_size, )
            current_page = int(offset / page_size) + 1
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