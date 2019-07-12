import numpy as np
import pandas as pd
import pytz
import ast
import itertools

from datetime import datetime as dt
from dateutil.parser import parse
from dateutil.tz import tzlocal
from django.db.models import Q, Count, Min, Sum, Avg
from django.db.models.functions import Concat
from django.core.paginator import Paginator
from bowlero_backend.settings import TIME_ZONE

from RM.Centers.models.models import *
from utils.UDatetime import UDatetime

from DAO.DataDAO import *
from RM.Pricing.models.models import *
from BowlingShoe.BSChangeReport.models.models import *

EST = pytz.timezone(TIME_ZONE)


class DataReviseDAO:

    @classmethod
    def pricing(cls, start, end, product_name, DOW, price_dict, centers, user):

        centers_len = len(centers)

        period_list = []
        for key, value in price_dict.items():
            if value[1]:
                period_list += [key]
        period_len = len(period_list)

        if centers_len == 0 or period_len == 0:
            return

        # date_list = list(itertools.chain.from_iterable(itertools.repeat(x, centers_len*period_len) for x in date_range))
        # centers_list = list(itertools.chain.from_iterable(itertools.repeat(x, centers_len*period_len) for x in date_range))
        # period_list = list(itertools.chain.from_iterable(itertools.repeat(x, centers_len*period_len) for x in date_range))

        from_records = cls.get_from_records(product_name, DOW, centers)
        # print(from_records)

        period_obj = Period.objects\
            .filter(
                center_id__in= centers,
                DOW__in=DOW,
                period_label__in=period_list,
                status='active'
            )
        period_records = pd.DataFrame.from_records(period_obj.values(
            'id',
            'DOW',
            'center_id',
            'start_time',
            'end_time',
            'overnight',
            'period_label',
        ))

        # find and set start price
        start_records = period_records
        start_records['price'] = None
        start_records['effective_datetime'] = start

        for index, row in start_records.iterrows():

            price_symbol = price_dict[row['period_label']][0]
            price_change = price_dict[row['period_label']][1]
            price_unit = price_dict[row['period_label']][2]
            period_base = price_dict[row['period_label']][3]
            price_records = from_records[
                (from_records['center_id'] == row['center_id']) &
                (from_records['period_label'] == period_base) &
                (from_records['DOW'] == row['DOW'])
                ]
            if not price_records.empty:
                price_base = price_records['price'].values[0]
                price_new = cls.price_converter(price_base, price_symbol, price_change, price_unit)
            else:
                price_new = None

            start_records.at[index, 'price'] = price_new

        start_records = start_records[start_records['price'].notnull()]

        #
        if start != end:
            end_records = period_records

        # load into database
        for index, row in start_records.iterrows():
            center_obj = Centers.objects.get(center_id=row['center_id'])
            if product_name == 'retail bowling':
                RetailBowlingPriceOld.objects \
                    .update_or_create(
                        effective_datetime=row['effective_datetime'],
                        start_time=row['start_time'],
                        end_time=row['end_time'],
                        center_id=center_obj,
                        DOW=row['DOW'],
                        product_name='retail bowling',
                        defaults={
                            'price': row['price'],
                            'period_label': row['period_label'],
                            'status': 'active',
                            'overnight': row['overnight'],
                            'create_user': user
                        }
                    )
            elif product_name == 'retail shoe':
                RetailShoePriceOld.objects \
                    .update_or_create(
                        effective_datetime=row['effective_datetime'],
                        start_time=row['start_time'],
                        end_time=row['end_time'],
                        center_id=center_obj,
                        DOW=row['DOW'],
                        product_name='retail bowling',
                        defaults={
                            'price': row['price'],
                            'period_label': row['period_label'],
                            'status': 'active',
                            'overnight': row['overnight'],
                            'create_user': user
                        }
                )


        # print(pd.DataFrame.from_records(period_records.values()))
        # for date in to_date_range:
        # for center in centers:
            # for period_label in period_list:
            #     if product_name == 'retail_bowling':
            #         price_detail = price_dict[period_label]
            #
            #         price_symbol = price_detail[0]
            #         price_change = price_detail[1]
            #         price_unit = price_detail[2]
            #         price_base_period_label = price_detail[3]
            #
            #         dow = DOW_choice[date.weekday()][0]
            #
            #         price_from = from_records[
            #             (from_records['dow'] == dow) &
            #             (from_records['center_id'] == center) &
            #             (from_records['period_label'] == price_base_period_label)
            #         ]
            #
            #         if price_from.empty:
            #             continue
            #
            #         price_base = price_from['price'].values[0]
            #         start_time = datetime.datetime.combine(date, pd.to_datetime(price_from['start_time'].values[0]).time())
            #         end_time = datetime.datetime.combine(date, pd.to_datetime(price_from['end_time'].values[0]).time())
            #
            #         price_new = cls.price_converter(price_base, price_symbol, price_change, price_unit)
            #
            #         center_id = Centers.objects.get(center_id=center)
            #         product = Product.objects.get(name='bowling', sell_type='retail')
            #         RetailBowlingPrice.objects.update_or_create(
            #             business_date=date,
            #             center_id=center_id,
            #             period_label=period_label,
            #             start_time=start_time,
            #             end_time=end_time,
            #             product=product,
            #             defaults={
            #                 'price': price_new
            #             }
            #         )
            #     elif product_name == 'retail_shoe':
            #         price_detail = price_dict[period_label]
            #
            #         price_symbol = price_detail[0]
            #         price_change = price_detail[1]
            #         price_unit = price_detail[2]
            #         price_base_period_label = price_detail[3]
            #
            #         dow = DOW_choice[date.weekday()][0]
            #
            #         price_from = from_records[
            #             (from_records['dow'] == dow) &
            #             (from_records['center_id'] == center) &
            #             (from_records['period_label'] == price_base_period_label)
            #         ]
            #
            #         if price_from.empty:
            #             continue
            #
            #         price_base = price_from['price'].values[0]
            #         start_time = datetime.datetime.combine(date, pd.to_datetime(price_from['start_time'].values[0]).time())
            #         end_time = datetime.datetime.combine(date, pd.to_datetime(price_from['end_time'].values[0]).time())
            #
            #         price_new = cls.price_converter(price_base, price_symbol, price_change, price_unit)
            #
            #         center_id = Centers.objects.get(center_id=center)
            #         product = Product.objects.get(name='shoe', sell_type='retail')
            #         RetailShoePrice.objects.update_or_create(
            #             business_date=date,
            #             center_id=center_id,
            #             period_label=period_label,
            #             start_time=start_time,
            #             end_time=end_time,
            #             product=product,
            #             defaults={
            #                 'price': price_new
            #             }
            #         )

        # print(start, end, product, DOW, price, centers)

    @classmethod
    def get_from_records(cls, product, DOW, centers):

        from_records = pd.DataFrame()

        today_date = UDatetime.now_local().date()
        # today_date = datetime.datetime(2018, 2, 19)
        from_date_range = UDatetime.week_range(today_date)

        if product == 'retail bowling':
            from_obj = RetailBowlingPriceOld.objects\
                .filter(
                    center_id__in=centers,
                    DOW__in=DOW,
                    status='active',
                    effective_datetime__lte=from_date_range[-1]
                )\
                .order_by(
                    '-effective_datetime'
                )

            from_records = pd.DataFrame.from_records(
                from_obj.values(
                    'id',
                    'price',
                    'effective_datetime',
                    'start_time',
                    'end_time',
                    'DOW',
                    'center_id',
                    'period',
                    'period_label',
                ))

        elif product == 'retail shoe':
            from_records_obj = RetailShoePriceOld.objects.filter(business_date__in=from_date_range).values(
                'price',
                'business_date',
                'start_time',
                'end_time',
                'center_id',
                'period',
                'period_label',
            )

            from_records = pd.DataFrame.from_records(from_records_obj)
            from_records['dow'] = from_records['business_date'].apply(lambda x: DOW_choice[x.weekday()][0])

        return from_records

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

    # bulk price based on last week's price and schedule
    @classmethod
    def pricing_new(cls, start, end, product_name, DOW, price, centers, current_user, tracking_id=None):

        centers_len = len(centers)
        if centers_len == 0:
            return

        if product_name == 'retail bowling':
            cls.pricing_retailbowling(start, end, product_name, DOW, price, centers, current_user,
                                      tracking_id=tracking_id)
        elif product_name == 'retail shoe':
            cls.pricing_retailshoe(start, end, product_name, DOW, price, centers, current_user,
                                   tracking_id=tracking_id)
        else:
            cls.pricing_product(start, end, product_name, DOW, price, centers, current_user,
                                tracking_id=tracking_id)

    @classmethod
    def pricing_retailbowling(cls, start, end, product_name, DOW, price, centers, current_user, tracking_id=None):
        period_list = []
        for key, value in price.items():
            if value[1]:
                period_list += [key]
        period_len = len(period_list)

        if period_len == 0:
            return

        to_date_range = UDatetime.date_range(start, end, DOW)

        from_records = cls.get_from_records_new(product_name, DOW, centers)
        to_records = pd.DataFrame()

        for date in to_date_range:
            dow = DOW_choice[date.weekday()][0]
            for center in centers:
                for period_label in period_list:
                    if period_label == 'non-prime':
                        product_ids = ProductChoice.retail_bowling_non_prime_product_ids
                    elif period_label == 'prime':
                        product_ids = ProductChoice.retail_bowling_prime_product_ids
                    elif period_label == 'premium':
                        product_ids = ProductChoice.retail_bowling_premium_product_ids
                    else:
                        continue

                    schedule_from = from_records[
                        (from_records['DOW'] == dow) &
                        (from_records['center_id'] == center) &
                        (from_records['product_id'].isin(product_ids))
                        ]

                    price_detail = price[period_label]
                    price_symbol = price_detail[0]
                    price_change = price_detail[1]
                    price_unit = price_detail[2]
                    price_base_period_label = price_detail[3]

                    if price_base_period_label == 'non-prime':
                        product_base_ids = ProductChoice.retail_bowling_non_prime_product_ids
                    elif price_base_period_label == 'prime':
                        product_base_ids = ProductChoice.retail_bowling_prime_product_ids
                    elif price_base_period_label == 'premium':
                        product_base_ids = ProductChoice.retail_bowling_premium_product_ids
                    else:
                        continue

                    price_from = from_records[
                        (from_records['DOW'] == dow) &
                        (from_records['center_id'] == center) &
                        (from_records['product_id'].isin(product_base_ids))
                    ]

                    if price_from.empty:
                        continue

                    price_base = price_from['price'].values[0]
                    price_new = cls.price_converter(price_base, price_symbol, price_change, price_unit)

                    schedule_from.loc[:, 'price_new'] = price_new
                    schedule_from.loc[:, 'date'] = date.date()

                    to_records = to_records.append(schedule_from)

        for index, row in to_records.iterrows():
            center_obj = Centers.objects.get(center_id=row['center_id'])
            product_obj = Product.objects.get(product_id=row['product_id'])

            RetailBowlingPrice.objects \
                .update_or_create(
                date=row['date'],
                DOW=row['DOW'],
                center_id=center_obj,
                product_id=product_obj,
                product_name=product_obj.product_name,
                defaults={
                    'price': round(row['price_new'], 2),
                    'action_user': current_user,
                    'tracking_id': tracking_id
                }
            )

            # Tracking Change Report
            BSChangeReport.objects.update_or_create\
            (
                tracking_id=tracking_id,
                username=current_user,
                center_id=center_obj,
                product_id=product_obj,
                effective_start=start,
                effective_end=end,
                price_old=row['price'],
                price_new=row['price_new'],
                is_bulk_change=True
            )

    @classmethod
    def pricing_retailshoe(cls, start, end, product_name, DOW, price, centers, current_user, tracking_id=None):

        to_date_range = UDatetime.date_range(start, end, DOW)

        from_records = cls.get_from_records_new(product_name, DOW, centers)
        to_records = pd.DataFrame()

        for date in to_date_range:
            dow = DOW_choice[date.weekday()][0]
            for center in centers:
                product_ids = ProductChoice.retail_shoe_product_ids

                schedule_from = from_records[
                    (from_records['DOW'] == dow) &
                    (from_records['center_id'] == center) &
                    (from_records['product_id'].isin(product_ids))
                    ]

                price_detail = price['price']
                price_symbol = price_detail[0]
                price_change = price_detail[1]
                price_unit = price_detail[2]

                price_from = from_records[
                    (from_records['DOW'] == dow) &
                    (from_records['center_id'] == center) &
                    (from_records['product_id'].isin(product_ids))
                ]

                if price_from.empty:
                    continue

                price_base = price_from['price'].values[0]
                price_new = cls.price_converter(price_base, price_symbol, price_change, price_unit)

                schedule_from.loc[:, 'price_new'] = price_new
                schedule_from.loc[:, 'date'] = date.date()

                to_records = to_records.append(schedule_from)

        for index, row in to_records.iterrows():
            center_obj = Centers.objects.get(center_id=row['center_id'])
            product_obj = Product.objects.get(product_id=row['product_id'])

            RetailShoePrice.objects \
                .update_or_create(
                date=row['date'],
                DOW=row['DOW'],
                center_id=center_obj,
                product_id=product_obj,
                product_name=product_obj.product_name,
                defaults={
                    'price': round(row['price_new'], 2),
                    'action_user': current_user,
                    'tracking_id': tracking_id
                }
            )

            # Tracking Change Report
            BSChangeReport.objects.update_or_create(
                tracking_id=tracking_id,
                username=current_user,
                center_id=center_obj,
                product_id=product_obj,
                effective_start=start,
                effective_end=end,
                price_old=row['price'],
                price_new=row['price_new'],
                is_bulk_change=True
            )

    @classmethod
    def pricing_product(cls, start, end, product_name, DOW, price, centers, current_user, tracking_id=None):

        to_date_range = UDatetime.date_range(start, end, DOW)

        from_records = cls.get_from_records_new(product_name, DOW, centers)
        if from_records.empty:
            return
        product_obj = Product.objects.get(product_name=product_name)
        product_id = product_obj.product_id

        to_records = pd.DataFrame()

        for date in to_date_range:
            dow = DOW_choice[date.weekday()][0]
            for center in centers:
                product_ids = [product_id]

                schedule_from = from_records[
                    (from_records['DOW'] == dow) &
                    (from_records['center_id'] == center) &
                    (from_records['product_id'].isin(product_ids))
                    ]

                price_detail = price['price']
                price_symbol = price_detail[0]
                price_change = price_detail[1]
                price_unit = price_detail[2]

                price_from = from_records[
                    (from_records['DOW'] == dow) &
                    (from_records['center_id'] == center) &
                    (from_records['product_id'].isin(product_ids))
                ]

                if price_from.empty:
                    continue

                price_base = price_from['price'].values[0]
                price_new = cls.price_converter(price_base, price_symbol, price_change, price_unit)

                schedule_from.loc[:, 'price_new'] = price_new
                schedule_from.loc[:, 'date'] = date.date()

                to_records = to_records.append(schedule_from)

        for index, row in to_records.iterrows():
            center_obj = Centers.objects.get(center_id=row['center_id'])
            # product_obj = Product.objects.get(product_id=row['product_id'])

            ProductPrice.objects \
                .update_or_create(
                    date=row['date'],
                    DOW=row['DOW'],
                    center_id=center_obj,
                    product_id=product_obj,
                    product_name=product_obj.product_name,
                    defaults={
                        'price': round(row['price_new'], 2),
                        'action_user': current_user,
                        ''
                        'tracking_id': tracking_id,
                    }
                )

            # Tracking Change Report
            BSChangeReport.objects.update_or_create(
                tracking_id=tracking_id,
                username=current_user,
                center_id=center_obj,
                product_id=product_obj,
                effective_start=start,
                effective_end=end,
                price_old=row['price'],
                price_new=row['price_new'],
                is_bulk_change=True
            )

    @classmethod
    def get_from_records_new(cls, product, DOW, centers):

        from_records = pd.DataFrame()

        today_date = UDatetime.now_local().date()
        # today_date = datetime.datetime(2018, 2, 19)
        from_date_range = UDatetime.week_range(today_date)

        if product == 'retail bowling':
            from_obj = RetailBowlingPrice.objects\
                .filter(
                    center_id__in=centers,
                    DOW__in=DOW,
                    date__in=from_date_range
                )\
                .order_by(
                    'date'
                )

            from_records = pd.DataFrame.from_records(
                from_obj.values(
                    'id',
                    'price',
                    'date',
                    'DOW',
                    'center_id',
                    'product_id',
                    'schedule',
                ))
        elif product == 'retail shoe':
            from_obj = RetailShoePrice.objects\
                .filter(
                    center_id__in=centers,
                    DOW__in=DOW,
                    date__in=from_date_range
                )\
                .order_by(
                    'date'
                )

            from_records = pd.DataFrame.from_records(
                from_obj.values(
                    'id',
                    'price',
                    'date',
                    'DOW',
                    'center_id',
                    'product_id',
                    'schedule',
                ))
        else:
            # print(product)
            from_obj = ProductPrice.objects\
                .filter(
                    center_id__in=centers,
                    DOW__in=DOW,
                    date__in=from_date_range,
                    product_name=product
                )\
                .order_by(
                    'date'
                )

            from_records = pd.DataFrame.from_records(
                from_obj.values(
                    'id',
                    'price',
                    'date',
                    'DOW',
                    'center_id',
                    'product_id',
                    'schedule',
                ))

        return from_records

    @staticmethod
    def get_period_label_from_product_id(product_id):
        if product_id in ProductChoice.retail_bowling_non_prime_product_ids:
            return 'non-prime'
        elif product_id in ProductChoice.retail_bowling_prime_product_ids:
            return 'prime'
        elif product_id in ProductChoice.retail_bowling_premium_product_ids:
            return 'premium'
        else:
            return None

    @staticmethod
    def get_product_id_from_period_label(period_label_list):

        product_ids = []
        if 'non-prime' in period_label_list:
            product_ids += ProductChoice.retail_bowling_non_prime_product_ids
        if 'prime' in period_label_list:
            product_ids += ProductChoice.retail_bowling_prime_product_ids
        if 'premium' in period_label_list:
            product_ids += ProductChoice.retail_bowling_premium_product_ids

        return product_ids

    # bulk price based on last price and product schedule and opt in/out
    @classmethod
    def pricing_new2(cls, start, end, product_name, DOW, price, centers, current_user, start_report, end_report,
                     tracking_id=None):

        if centers[0] == '':
            return

        if product_name == 'retail bowling':
            cls.pricing_retailbowling2(start, end, product_name, DOW, price, centers, current_user,
                                       start_report, end_report, tracking_id=tracking_id)
        elif product_name == 'Retail Shoe':
            cls.pricing_retailshoe2(start, end, product_name, DOW, price, centers, current_user,
                                    start_report, end_report, tracking_id=tracking_id)
        else:
            cls.pricing_product2(start, end, product_name, DOW, price, centers, current_user,
                                 start_report, end_report, tracking_id=tracking_id)

    @classmethod
    def pricing_retailbowling2(cls, start, end, product_name, DOW, price, centers, current_user,
                               start_report, end_report, tracking_id=None):

        # find change product and based product
        period_list = []
        base_list = []
        for key, value in price.items():
            if value[1] or value[1] == 0:
                period_list += [key]
                base_list += [value[3]]
        base_list = list(set(base_list))
        if period_list == 0:
            return

        total_list = list(set(period_list + base_list))

        # get last price
        if not total_list:
            return
        total_product_ids = cls.get_product_id_from_period_label(total_list)
        last_price_records = DataDAO.LastPrice.get_last_price(total_product_ids, centers)
        if last_price_records.empty:
            return

        # get product schedule
        change_product_ids = cls.get_product_id_from_period_label(period_list)
        productschedule_obj = ProductSchedule.objects.filter(product_id__product_id__in=change_product_ids,
                                                             status='active')
        productschedule_records = pd.DataFrame.from_records(productschedule_obj.values('product_id__product_id','DOW'))
        productschedule_records.rename({'product_id__product_id': 'product_id'}, axis=1, inplace=True)

        productopt_obj = ProductOpt.objects.filter(product_id__product_id__in=change_product_ids,
                                                   center_id__center_id__in=centers)
        productopt_records = pd.DataFrame.from_records(productopt_obj.values('product_id__product_id',
                                                                             'center_id__center_id',
                                                                             'opt'))
        productopt_records.rename({'product_id__product_id': 'product_id',
                                   'center_id__center_id': 'center_id'
                                   }, axis=1, inplace=True)

        centers_obj = Centers.objects.filter(center_id__in=centers)
        centers_record = pd.DataFrame.from_records(centers_obj.values('center_id', 'center_type'))

        to_date_range_org = UDatetime.date_range(start, end, DOW)
        to_records_list = []

        for center in centers:
            center_type = centers_record[centers_record['center_id'] == center].iloc[0]['center_type']
            for period_label in period_list:
                product_id = ProductChoice.retail_bowling_map[period_label][center_type]
                to_date_range = to_date_range_org

                # get opt
                if period_label == 'prime':
                    product_opt = productopt_records[(productopt_records['product_id'] == product_id) &
                                                     (productopt_records['center_id'] == center)
                                                     ]
                    if product_opt.empty:
                        continue
                    product_opt = product_opt.iloc[0]['opt']
                    if product_opt == 'Out':
                        to_date_range = [date for date in to_date_range_org if date.weekday() in [4, 5, 6]]

                elif period_label == 'premium':
                    product_opt = productopt_records[(productopt_records['product_id'] == product_id) &
                                                     (productopt_records['center_id'] == center)
                                                    ]
                    if product_opt.empty:
                        continue
                    product_opt = product_opt.iloc[0]['opt']
                    if product_opt == 'Out':
                        continue

                # get schedule
                productschedule = productschedule_records[productschedule_records['product_id'] == product_id]
                if productschedule.empty:
                    continue
                productschedule = productschedule['DOW'].unique()
                to_date_range = [date for date in to_date_range if DOW_choice[date.weekday()][0] in productschedule]

                price_detail = price[period_label]
                price_symbol = price_detail[0]
                price_change = price_detail[1]
                price_unit = price_detail[2]
                price_base_period_label = price_detail[3]

                # get price
                if price_base_period_label:
                    product_base_id = ProductChoice.retail_bowling_map[price_base_period_label][center_type]

                    price_base = last_price_records[(last_price_records['product_id'] == product_base_id) &
                                                    (last_price_records['center_id'] == center)
                                                    ]
                    if price_base.empty:
                        continue

                    price_base = price_base.iloc[0]['price']
                else:
                    price_base = None
                price_new = cls.price_converter(price_base, price_symbol, price_change, price_unit)

                if to_date_range:

                    price_old = last_price_records[(last_price_records['product_id'] == product_id) &
                                                   (last_price_records['center_id'] == center)
                                                   ]
                    if price_old.empty:
                        price_old = None
                    else:
                        price_old = price_old.iloc[0]['price']

                    to_records_list += \
                    [
                        {
                            'center_id': center,
                            'product_id': product_id,
                            'date': date,
                            'DOW': DOW_choice[date.weekday()][0],
                            'price_old': price_old,
                            'price_new': price_new
                         }
                        for date in to_date_range
                     ]

                else:
                    continue

        to_records = pd.DataFrame(to_records_list)

        for index, row in to_records.iterrows():
            center_obj = Centers.objects.get(center_id=row['center_id'])
            product_obj = Product.objects.get(product_id=row['product_id'])

            RetailBowlingPrice.objects \
                .update_or_create(
                    date=row['date'],
                    DOW=row['DOW'],
                    center_id=center_obj,
                    product_id=product_obj,
                    product_name=product_obj.product_name,
                    defaults={
                        'price': round(row['price_new'], 2),
                        'action_user': current_user,
                        'tracking_id': tracking_id
                    }
                )

            # Tracking Change Report
            BSChangeReport.objects \
                .update_or_create(
                    tracking_id=tracking_id,
                    username=current_user,
                    center_id=center_obj,
                    product_id=product_obj,
                    effective_start=start_report,
                    effective_end=end_report,
                    price_old=row['price_old'],
                    price_new=row['price_new'],
                    is_bulk_change=True
                )

    @classmethod
    def pricing_retailshoe2(cls, start, end, product_name, DOW, price, centers, current_user, start_report, end_report,
                            tracking_id=None):

        # find change product and price
        price_list = []
        for key, value in price.items():
            if value[1] or value[1] == 0:
                price_list += [value[1]]
        if not price_list:
            return

        product_obj = Product.objects.get(readable_product_name__contains=product_name)
        product_id = product_obj.product_id

        # get last price
        last_price_records = DataDAO.LastPrice.get_last_price([product_id], centers)
        if last_price_records.empty:
            return

        # get product schedule
        productschedule_obj = ProductSchedule.objects.filter(product_id__product_id=product_id,
                                                             status='active')
        productschedule_records = pd.DataFrame.from_records(productschedule_obj.values('product_id__product_id', 'DOW'))
        productschedule_records.rename({'product_id__product_id': 'product_id'}, axis=1, inplace=True)

        productopt_obj = ProductOpt.objects.filter(product_id__product_id=product_id,
                                                   center_id__center_id__in=centers)

        productopt_records = pd.DataFrame.from_records(productopt_obj.values('product_id__product_id',
                                                                             'center_id__center_id',
                                                                             'opt'))
        productopt_records.rename({'product_id__product_id': 'product_id',
                                   'center_id__center_id': 'center_id'
                                   }, axis=1, inplace=True)

        centers_obj = Centers.objects.filter(center_id__in=centers)
        centers_record = pd.DataFrame.from_records(centers_obj.values('center_id', 'center_type'))

        to_date_range_org = UDatetime.date_range(start, end, DOW)
        to_records_list = []

        for center in centers:
            to_date_range = to_date_range_org

            # get opt
            if not productopt_records.empty:
                product_opt = productopt_records[(productopt_records['product_id'] == product_id) &
                                                 (productopt_records['center_id'] == center)
                                                 ]
                if product_opt.empty:
                    continue
                product_opt = product_opt.iloc[0]['opt']
                if product_opt == 'Out':
                    continue

            # get schedule
            productschedule = productschedule_records[productschedule_records['product_id'] == product_id]
            if productschedule.empty:
                continue
            productschedule = productschedule['DOW'].unique()
            to_date_range = [date for date in to_date_range if DOW_choice[date.weekday()][0] in productschedule]

            price_detail = price['price']
            price_symbol = price_detail[0]
            price_change = price_detail[1]
            price_unit = price_detail[2]

            # get price
            price_base = last_price_records[(last_price_records['product_id'] == product_id) &
                                            (last_price_records['center_id'] == center)
                                            ]
            if price_base.empty:
                continue

            price_base = price_base.iloc[0]['price']

            price_new = cls.price_converter(price_base, price_symbol, price_change, price_unit)

            if to_date_range:

                price_old = last_price_records[(last_price_records['product_id'] == product_id) &
                                               (last_price_records['center_id'] == center)
                                               ]
                if price_old.empty:
                    price_old = None
                else:
                    price_old = price_old.iloc[0]['price']

                to_records_list += \
                    [
                        {
                            'center_id': center,
                            'product_id': product_id,
                            'date': date,
                            'DOW': DOW_choice[date.weekday()][0],
                            'price_old': price_old,
                            'price_new': price_new
                        }
                        for date in to_date_range
                    ]

            else:
                continue

        to_records = pd.DataFrame(to_records_list)
        for index, row in to_records.iterrows():
            center_obj = Centers.objects.get(center_id=row['center_id'])
            product_obj = Product.objects.get(product_id=row['product_id'])

            RetailShoePrice.objects \
                .update_or_create(
                    date=row['date'],
                    DOW=row['DOW'],
                    center_id=center_obj,
                    product_id=product_obj,
                    product_name=product_obj.product_name,
                    defaults={
                        'price': round(row['price_new'], 2),
                        'action_user': current_user,
                        'tracking_id': tracking_id
                    }
                )

            # Tracking Change Report
            BSChangeReport.objects \
                .update_or_create(
                    tracking_id=tracking_id,
                    username=current_user,
                    center_id=center_obj,
                    product_id=product_obj,
                    effective_start=start_report,
                    effective_end=end_report,
                    price_old=row['price_old'],
                    price_new=row['price_new'],
                    is_bulk_change=True
                )

    @classmethod
    def pricing_product2(cls, start, end, product_name, DOW, price, centers, current_user, start_report, end_report,
                         tracking_id=None):

        # find change product and price
        price_list = []
        for key, value in price.items():
            if value[1] or value[1] == 0:
                price_list += [value[1]]
        if not price_list:
            return

        product_obj = Product.objects.get(readable_product_name__contains=product_name)
        product_id = product_obj.product_id

        # get last price
        last_price_records = DataDAO.LastPrice.get_last_price([product_id], centers)
        if last_price_records.empty:
            return

        # get product schedule
        productschedule_obj = ProductSchedule.objects.filter(product_id__product_id=product_id,
                                                             status='active')
        productschedule_records = pd.DataFrame.from_records(productschedule_obj.values('product_id__product_id', 'DOW'))
        productschedule_records.rename({'product_id__product_id': 'product_id'}, axis=1, inplace=True)

        productopt_obj = ProductOpt.objects.filter(product_id__product_id=product_id,
                                                   center_id__center_id__in=centers)

        productopt_records = pd.DataFrame.from_records(productopt_obj.values('product_id__product_id',
                                                                             'center_id__center_id',
                                                                             'opt'))
        productopt_records.rename({'product_id__product_id': 'product_id',
                                   'center_id__center_id': 'center_id'
                                   }, axis=1, inplace=True)

        centers_obj = Centers.objects.filter(center_id__in=centers)
        centers_record = pd.DataFrame.from_records(centers_obj.values('center_id', 'center_type'))

        to_date_range_org = UDatetime.date_range(start, end, DOW)
        to_records_list = []

        for center in centers:
            to_date_range = to_date_range_org

            # get opt
            if not productopt_records.empty:
                product_opt = productopt_records[(productopt_records['product_id'] == product_id) &
                                                 (productopt_records['center_id'] == center)
                                                 ]
                if product_opt.empty:
                    continue
                product_opt = product_opt.iloc[0]['opt']
                if product_opt == 'Out':
                    continue

            # get schedule
            productschedule = productschedule_records[productschedule_records['product_id'] == product_id]
            if productschedule.empty:
                continue
            productschedule = productschedule['DOW'].unique()
            to_date_range = [date for date in to_date_range if DOW_choice[date.weekday()][0] in productschedule]

            price_detail = price['price']
            price_symbol = price_detail[0]
            price_change = price_detail[1]
            price_unit = price_detail[2]

            # get price
            price_base = last_price_records[(last_price_records['product_id'] == product_id) &
                                            (last_price_records['center_id'] == center)
                                            ]
            if price_base.empty:
                continue

            price_base = price_base.iloc[0]['price']

            price_new = cls.price_converter(price_base, price_symbol, price_change, price_unit)

            if to_date_range:

                price_old = last_price_records[(last_price_records['product_id'] == product_id) &
                                               (last_price_records['center_id'] == center)
                                               ]
                if price_old.empty:
                    price_old = None
                else:
                    price_old = price_old.iloc[0]['price']

                to_records_list += \
                    [
                        {
                            'center_id': center,
                            'product_id': product_id,
                            'date': date,
                            'DOW': DOW_choice[date.weekday()][0],
                            'price_old': price_old,
                            'price_new': price_new
                        }
                        for date in to_date_range
                    ]

            else:
                continue

        to_records = pd.DataFrame(to_records_list)

        for index, row in to_records.iterrows():
            center_obj = Centers.objects.get(center_id=row['center_id'])
            product_obj = Product.objects.get(product_id=row['product_id'])

            ProductPrice.objects \
                .update_or_create(
                    date=row['date'],
                    DOW=row['DOW'],
                    center_id=center_obj,
                    product_id=product_obj,
                    product_name=product_obj.product_name,
                    defaults={
                        'price': round(row['price_new'], 2),
                        'action_user': current_user,
                        'tracking_id': tracking_id
                    }
                )

            # Tracking Change Report
            BSChangeReport.objects \
                .update_or_create(
                    tracking_id=tracking_id,
                    username=current_user,
                    center_id=center_obj,
                    product_id=product_obj,
                    effective_start=start_report,
                    effective_end=end_report,
                    price_old=row['price_old'],
                    price_new=row['price_new'],
                    is_bulk_change=True
                )

    # bulk price based on last price and product schedule and opt in/out
    @classmethod
    def pricing_new3(cls, start, end, product_id, DOW, price, centers, current_user, start_report, end_report,
                     tracking_id=None):

        if centers[0] == '':
            return

        if product_id == 'retail bowling':
            cls.pricing_product3(start, end, product_id, DOW, price, centers, current_user,
                                 start_report, end_report, tracking_id=tracking_id, model=RetailBowlingPrice)
        elif product_id == 'retail shoe':
            cls.pricing_product3(start, end, product_id, DOW, price, centers, current_user,
                                 start_report, end_report, tracking_id=tracking_id, model=RetailShoePrice)
        else:
            cls.pricing_product3(start, end, product_id, DOW, price, centers, current_user,
                                 start_report, end_report, tracking_id=tracking_id, model=ProductPrice)
#current version being used
    @classmethod
    def pricing_new4(cls, start, end, product_id, DOW, price, centers, current_user, tracking_id=None):

        if centers[0] == '':
            return

        price_records = pd.DataFrame(price)
        price_records = price_records[~price_records['price_delta'].isna()]

        product_ids = list(price_records['product_id'].values)
        product_ids_base = list(price_records['product_id_base'].values)
        total_product_ids = list(set(product_ids + product_ids_base))

        # get last price
        if not total_product_ids:
            return
        last_price_records = PriceChange.get_last_price(total_product_ids, centers, start)
        if not last_price_records.empty:
            last_price_records = last_price_records[['center_id', 'product_id', 'price']]

        # init to_records
        if DOW:
            to_records_list = [
                {'center_id': center_id, 'product_id': product_id, 'DOW': dow}
                for center_id in centers
                for product_id in product_ids
                for dow in DOW
            ]
        else:
            to_records_list = [
                {'center_id': center_id, 'product_id': product_id, 'DOW': None}
                for center_id in centers
                for product_id in product_ids
            ]
        to_records = pd.DataFrame(to_records_list)

        # get new price
        to_records = to_records.join(price_records.set_index(['product_id']), on=['product_id'], how='left')
        if not last_price_records.empty:
            last_price_records.rename({'price': 'price_old'}, axis=1, inplace=True)
            to_records = to_records.join(last_price_records.set_index(['center_id', 'product_id']),
                                         on=['center_id', 'product_id'], how='left')
            last_price_records.rename({'price_old': 'price_base', 'product_id': 'product_id_base'},
                                      axis=1, inplace=True)
            to_records = to_records.join(last_price_records.set_index(['center_id', 'product_id_base']),
                                         on=['center_id', 'product_id_base'], how='left')
            to_records = to_records.where((pd.notnull(to_records)), None)
        else:
            to_records['price_old'] = None
            to_records['price_base'] = None

        to_records['price_new'] = to_records[['price_base', 'price_symbol', 'price_delta', 'price_unit']] \
            .apply(lambda x: cls.price_converter(x['price_base'], x['price_symbol'],
                                                 x['price_delta'], x['price_unit']),
                   axis=1)

        # get price perpetual
        if end:
            perpetual = False
        else:
            perpetual = True
        to_records['perpetual'] = perpetual

        # Load into database
        for index, row in to_records.iterrows():
            center_obj = Centers.objects.get(center_id=row['center_id'])
            product_obj = Product.objects.get(product_id=row['product_id'])

            ProductPriceChange.objects \
                .update_or_create(
                    start=start,
                    end=end,
                    # DOW=row['DOW'],
                    center_id=center_obj,
                    product_id=product_obj,
                    action_time=UDatetime.now_local(),
                    defaults={
                        'price': round(row['price_new'], 2),
                        'perpetual': row['perpetual'],
                        'product_name': product_obj.product_name,
                        'action_user': current_user,
                        'tracking_id': tracking_id,
                    }
                )

            BSChangeReport.objects \
                .update_or_create(
                        tracking_id=tracking_id,
                        username=current_user,
                        center_id=center_obj,
                        product_id=product_obj,
                        effective_start=start,
                        effective_end=end,
                        price_old=row['price_old'],
                        price_new=row['price_new'],
                        is_bulk_change=True,
                        action_time=UDatetime.now_local()
                )

            # Add change record for retail wk-prime opt out and wknd-premium opt out
            product_id = row['product_id']
            product_map = {'108': '109', '111': '112'}
            if product_id in ['108', '111']:
                product_oppo = product_map[product_id]
                product_obj_oppo = Product.objects.get(product_id=product_oppo)
                BSChangeReport.objects \
                    .update_or_create(
                            tracking_id=tracking_id,
                            username=current_user,
                            center_id=center_obj,
                            product_id=product_obj_oppo,
                            effective_start=start,
                            effective_end=end,
                            price_old=row['price_old'],
                            price_new=row['price_new'],
                            is_bulk_change=True,
                            action_time=UDatetime.now_local()
                    )

        return

    @classmethod
    def pricing_product3(cls, start, end, product_id, DOW, price, centers, current_user,
                         start_report, end_report, tracking_id=None, model=None):

        price_records = pd.DataFrame(price)
        price_records = price_records[~price_records['price_delta'].isna()]

        product_ids = list(price_records['product_id'].values)
        product_ids_base = list(price_records['product_id_base'].values)
        total_product_ids = list(set(product_ids + product_ids_base))
        # get last price
        if not total_product_ids:
            return
        last_price_records = DataDAO.LastPrice.get_last_price(total_product_ids, centers, start)
        if not last_price_records.empty:
            last_price_records = last_price_records[['center_id', 'product_id', 'price']]

        # init to_records
        to_date_range = UDatetime.date_range(start, end, DOW)

        if not to_date_range:
            return
        to_records_list = [
            {'center_id': center_id, 'product_id': product_id, 'date': date,
             'DOW': DOW_choice[date.weekday()][0]}
            for center_id in centers
            for product_id in product_ids
            for date in to_date_range
        ]
        to_records = pd.DataFrame(to_records_list)

        # get product schedule
        productschedule_obj = ProductSchedule.objects.filter(product_id__product_id__in=product_ids,
                                                             status='active')
        productschedule_records = pd.DataFrame.from_records(productschedule_obj.values('product_id__product_id',
                                                                                       'DOW'))
        productschedule_records.rename({'product_id__product_id': 'product_id'}, axis=1, inplace=True)
        productschedule_records.drop_duplicates(['product_id', 'DOW'], inplace=True)
        productschedule_records['available'] = True

        to_records = to_records.join(productschedule_records.set_index(['product_id', 'DOW']),
                                     on=['product_id', 'DOW'], how='left')

        # Get product opt in / out
        productopt_records = ProductOptGet.get_productopt(product_ids, start, end, centers)
        if productopt_records.empty:
            return

        to_records['date'] = to_records['date'].apply(lambda x: str(x))
        productopt_records['date'] = productopt_records['date'].apply(lambda x: str(x))

        to_records = to_records.join(productopt_records.set_index(['center_id', 'product_id', 'date']),
                                     on=['center_id', 'product_id', 'date'], how='left')

        to_records = to_records[(to_records['available']) & (to_records['opt'] == 'In')]
        if to_records.empty:
            return

        # get new price
        to_records = to_records.join(price_records.set_index(['product_id']),
                                     on=['product_id'], how='left')
        if not last_price_records.empty:
            last_price_records.rename({'price': 'price_old'}, axis=1, inplace=True)
            to_records = to_records.join(last_price_records.set_index(['center_id', 'product_id']),
                                         on=['center_id', 'product_id'], how='left')
            last_price_records.rename({'price_old': 'price_base', 'product_id': 'product_id_base'},
                                      axis=1, inplace=True)
            to_records = to_records.join(last_price_records.set_index(['center_id', 'product_id_base']),
                                         on=['center_id', 'product_id_base'], how='left')
            to_records = to_records.where((pd.notnull(to_records)), None)
        else:
            to_records['price_old'] = None
            to_records['price_base'] = None

        to_records['price_new'] = to_records[['price_base', 'price_symbol', 'price_delta', 'price_unit']] \
            .apply(lambda x: cls.price_converter(x['price_base'], x['price_symbol'],
                                                 x['price_delta'], x['price_unit']),
                   axis=1)

        # get price perpetual
        if end_report:
            perpetual = False
        else:
            perpetual = True

        to_records['perpetual'] = perpetual
        to_records_nodate = to_records.drop_duplicates(['center_id', 'product_id'])

        # Load into database
        for index, row in to_records.iterrows():
            center_obj = Centers.objects.get(center_id=row['center_id'])
            product_obj = Product.objects.get(product_id=row['product_id'])

            model.objects \
                .update_or_create(
                    date=row['date'],
                    DOW=row['DOW'],
                    center_id=center_obj,
                    product_id=product_obj,
                    defaults={
                        'price': round(row['price_new'], 2),
                        'perpetual': row['perpetual'],
                        'product_name': product_obj.product_name,
                        'action_user': current_user,
                        'tracking_id': tracking_id,
                        'action_time': UDatetime.now_local()
                    }
                )

        for index, row in to_records_nodate.iterrows():
            # Tracking Change Report
            center_obj = Centers.objects.get(center_id=row['center_id'])
            product_obj = Product.objects.get(product_id=row['product_id'])
            BSChangeReport.objects \
                .update_or_create(
                    tracking_id=tracking_id,
                    username=current_user,
                    center_id=center_obj,
                    product_id=product_obj,
                    effective_start=start_report,
                    effective_end=end_report,
                    price_old=row['price_old'],
                    price_new=row['price_new'],
                    is_bulk_change=True,
                    action_time=UDatetime.now_local()
                )

            # Overwrite future price if perpetual
            if perpetual:
                model.objects \
                    .filter(center_id=center_obj,
                            product_id=product_obj,
                            date__gt=end
                            ) \
                    .update(
                        price=round(row['price_new'], 2),
                        perpetual=row['perpetual'],
                        action_user=current_user,
                        tracking_id=tracking_id,
                        action_time=UDatetime.now_local()
                    )


class AlcoholReviseDAO:

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

    @classmethod
    def bulk_pricing(cls, start, end, price, date, price_type, categories, tiers, current_user, tracking_id=None):

        price_records = pd.DataFrame(price)
        price_records = price_records[~price_records['price_delta'].isna()]

        # get last price
        if price_records.empty:
            return
        last_price_records, num = AlcoholGet.get_alcoholtier(date, price_type, categories=categories, tiers=tiers,
                                                             add_dollar_symbol=False)
        last_price_records = pd.melt(last_price_records,
                                     id_vars=['action_time', 'category', 'category_id', 'level'],
                                     var_name='tier')

        last_price_records['value_new'] = last_price_records[['value']] \
            .apply(lambda x: cls.price_converter(x['value'], price_records['price_symbol'][0],
                                                 price_records['price_delta'][0], price_records['price_unit'][0]),
                   axis=1)

        # Load into database
        for index, row in last_price_records.iterrows():
            AlcoholTier.objects \
                .update_or_create(
                    category_id=row['category_id'],
                    tier=row['tier'],
                    price_type=price_type,
                    defaults={
                        'price': round(row['value_new'], 2),
                        'tier': row['tier'],
                        'start': start,
                        'end': end,
                        'action_user': current_user,
                        'tracking_id': tracking_id,
                        'action_time': UDatetime.now_local()
                    }
                )
