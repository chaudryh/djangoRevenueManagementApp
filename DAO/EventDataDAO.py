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
from Models.models.models import *
from utils.UDatetime import UDatetime


class EventDataDao:
    @classmethod
    def get_event_RMPS(cls, sale_region, territory, center_id, center_name, columns,
                       pagination=False, page_size=None, offset=None, filters=None, sort=None, order=None):
        if sort and order:
            # if sort == 'OLD':
            #     sort = 'create_date'
            # elif sort == 'balance_hour':
            #     sort = 'estimate_hour'
            if order == 'desc':
                sort = '-' + sort
        else:
            sort = 'center_id'

        centers = Centers.objects \
            .filter(status='open')

        if sale_region:
            centers = centers.filter(sale_region__in=sale_region)
        if territory:
            centers = centers.filter(territory__in=territory)
        if center_id:
            centers = centers.filter(center_id__in=center_id)
        if center_name:
            centers = centers.filter(center_id__in=center_name)
        centers = centers \
            .extra(select={'center_id': 'CAST(center_id AS INTEGER)'}) \
            .order_by(sort)

        # if filters:
        #     filters = ast.literal_eval(filters)
        #
        #     for key, value in filters.items():
        #         filters_list = value.split(',')
        #         filters_list = [x.strip() for x in filters_list]
        #         filters[key] = filters_list
        #     if filters.get('center_id'):
        #         filter_item = filters.get('center_id')
        #         if len(filter_item) == 1:
        #             centers = centers.filter(center_id__icontains=filter_item[0])
        #         else:
        #             centers = centers.filter(center_id__in=filter_item)
        #     if filters.get('center_name'):
        #         filter_item = filters.get('center_name')
        #         if len(filter_item) == 1:
        #             centers = centers.filter(center_name__icontains=filter_item[0])
        #         else:
        #             centers = centers.filter(reduce(operator.or_, (Q(center_name__icontains=item)
        #                                                            for item in filter_item if item)))
        #     if filters.get('sale_region'):
        #         filter_item = filters.get('sale_region')
        #         if len(filter_item) == 1:
        #             centers = centers.filter(sale_region__icontains=filter_item[0])
        #         else:
        #             centers = centers.filter(reduce(operator.or_, (Q(sale_region__icontains=item)
        #                                                            for item in filter_item if item)))
        #     if filters.get('territory'):
        #         filter_item = filters.get('territory')
        #         if len(filter_item) == 1:
        #             centers = centers.filter(territory__icontains=filter_item[0])
        #         else:
        #             centers = centers.filter(reduce(operator.or_, (Q(territory__icontains=item)
        #                                                            for item in filter_item if item)))
        #     if filters.get('arcade_type'):
        #         filter_item = filters.get('arcade_type')
        #         if len(filter_item) == 1:
        #             centers = centers.filter(arcade_type__icontains=filter_item[0])
        #         else:
        #             centers = centers.filter(reduce(operator.or_, (Q(arcade_type__icontains=item)
        #                                                            for item in filter_item if item)))

        num = centers.count()

        if pagination:
            paginator = Paginator(centers, page_size, )
            current_page = int(offset / page_size) + 1
            centers = paginator.page(current_page).object_list

        centers_record = pd.DataFrame.from_records(centers
                                                   .values('center_id',
                                                           'center_name',
                                                           'sale_region',
                                                           'territory',
                                                           'arcade_type',
                                                           ))

        if centers_record.empty:
            return pd.DataFrame(), num

        if columns:
            RMPSObjs = RMPS.objects \
                .filter(reduce(operator.or_, (Q(attribute__startswith=column + '---')
                                              for column in columns if column)))
        else:
            RMPSObjs = RMPS.objects.filter()

        RMPSRecords = pd.DataFrame.from_records(RMPSObjs.values(
            'center_id',
            'attribute',
            'value',
            'unit',
        ))

        # Format price to 2 decimals and add $
        RMPSRecords['value'] = RMPSRecords[['value', 'unit']] \
            .apply(lambda x: '${0:.2f}'.format(float(x['value'])) if x['unit'] == 'dollar'and
                                                                     x['value'] and
                                                                     x['value'].replace('.','').isdigit()
                                                                else x['value'], axis=1)

        RMPSRecords = pd.pivot_table(RMPSRecords,
                                     index=['center_id'],
                                     columns=['attribute'],
                                     values=['value'],
                                     aggfunc='first'
                                     )

        RMPSRecords.columns = RMPSRecords.columns.droplevel(0)
        RMPSRecords.columns.name = None
        RMPSRecords.reset_index(inplace=True)

        RMPSRecords['center_id'] = RMPSRecords['center_id'].apply(int)
        centers_record = centers_record.join(RMPSRecords.set_index(['center_id']),
                                             on=['center_id'], how='left')
        centers_record['Holiday Hours Hidden---'] = None

        return centers_record, num
