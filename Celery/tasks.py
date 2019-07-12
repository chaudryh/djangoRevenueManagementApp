from bowlero_backend.celery import app
import os
import sys
import datetime
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
import django
# from bbu.settings import BASE_DIR, MEDIA_ROOT

os.environ['DJANGO_SETTINGS_MODULE'] = 'bowlero_backend.settings'
django.setup()

from DAO.DataReviseDAO import DataReviseDAO
from DAO.FoodDAO import FoodDataDao
from utils.UDatetime import UDatetime

from accounts.models import *
from Audit.models.models import *
from Models.models.models import *
from BowlingShoe.BSChangeReport.models.models import *
from Food.FoodByCenter.models.models import *


@app.task
def bulk_price_change_task(start, end, product, DOW, price, centers, user,
                           tracking_id):
    start = UDatetime.datetime_str_init(start)
    start_report = start

    if not end:
        end = max(UDatetime.now_local() + datetime.timedelta(days=13),
                  start + datetime.timedelta(days=13))
        end_report = None
    else:
        end = UDatetime.datetime_str_init(end)
        end_report = end

    start = start.date()
    end = end.date()

    user = User.objects.get(username=user)
    tracking_id = Tracking.objects.get(tracking_id=tracking_id)

    DataReviseDAO.pricing_new3(start, end, product, DOW, price, centers, user,
                               start_report, end_report, tracking_id=tracking_id)

    return


@app.task
def bulk_price_change_task_from_price_change(start, end, product, DOW, price, centers, user,
                                             tracking_id):

    start = UDatetime.datetime_str_init(start).date()
    if not end:
        end = None
    else:
        end = UDatetime.datetime_str_init(end).date()

    user = User.objects.get(username=user)
    tracking_id = Tracking.objects.get(tracking_id=tracking_id)

    DataReviseDAO.pricing_new4(start, end, product, DOW, price, centers, user,
                               tracking_id=tracking_id)

    return


@app.task
def bulk_product_opt(data, current_user, start, end):

    data = pd.DataFrame.from_dict(data)
    current_user = User.objects.get(username=current_user)

    # Format Date
    start = UDatetime.datetime_str_init(start).date()
    if not end:
        end = None
    else:
        end = UDatetime.datetime_str_init(end).date()

    def update_opt(current_user, center_id, product_num, opt, start, end):
        center_obj = Centers.objects.get(center_id=center_id)
        product_obj = Product.objects.get(product_num=str(product_num))

        # Tracking
        tracking_type = TrackingType.objects.get(type='product opt in/out change')
        content_type = ContentType.objects.get_for_model(ProductOpt)
        input_params = {'opt': opt, 'center_id': center_id, 'start': str(start), 'end': str(end),
                        'product_num': product_num}
        tracking_id = Tracking.objects.create(
            username=current_user,
            tracking_type=tracking_type,
            content_type=content_type,
            input_params=input_params
        )
        # Tracking Change Report
        BSChangeReport.objects.create(
            tracking_id=tracking_id,
            username=current_user,
            center_id=center_obj,
            product_id=product_obj,
            effective_start=start,
            effective_end=end,
            price_old=None,
            price_new=None,
            is_bulk_change=True,
            opt=opt
        )
        #

        ProductOpt.objects \
            .update_or_create(
                product_id=product_obj,
                center_id=center_obj,
                start=start,
                end=end,
                defaults={
                    'opt': opt,
                    'action_user': current_user,
                    'tracking_id': tracking_id,
                    'action_time': UDatetime.now_local()
                }
            )

    for index, row in data.iterrows():
        center_id = row['center_id']
        product_num = row['product_num']
        opt = row['opt']

        update_opt(current_user, center_id, product_num, opt, start, end)

        # retail bowling opt in/out
        if product_num in ProductChoice.products_opt_oppo_pixel:
            if opt == 'In':
                opt_oppo = 'Out'
            elif opt == 'Out':
                opt_oppo = 'In'
            else:
                continue
            product_num_oppo = ProductChoice.products_opt_oppo_dict_pixel[product_num]
            update_opt(current_user, center_id, product_num_oppo, opt_oppo, start, end)
    return


@app.task
def update_food_price(menu_id, category_products, centers, start, end, price, category, user, tracking_id):

    user = User.objects.get(username=user)
    start = UDatetime.datetime_str_init(start).date() if start else UDatetime.now_local().date()
    end = UDatetime.datetime_str_init(start).date() if end else None

    FoodDataDao.updateFoodPrice(menu_id, category_products, centers, start, end, price, category, user, tracking_id)

    return

@app.task
def bulk_update_test(data):
    # Default for loop loops through columns and selects a whole column each time.
    # Iterrows is used to loop through rows
    data = pd.DataFrame.from_dict(data)

    for i, row in data.iterrows():
        # need to select 0 index bc values() returns a list with one item
        dbval = Centers.objects.filter(center_id__exact=row['center_id']) \
            .values_list(row['Sort by'], flat=True)[0]
        fileval = row['value']
        if dbval != fileval:
            # print(dbval, fileval)
            Centers.objects.filter(center_id__exact=row['center_id']) \
                .update(**{
                row['Sort by']: fileval,
            })

    return


