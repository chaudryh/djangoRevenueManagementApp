import os
import sys
import numpy as np
import pandas as pd
import re
from datetime import datetime as dt
import pytz
import time
import math

# sys.path.append('../..')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)
import django
# from bbu.settings import BASE_DIR, MEDIA_ROOT

os.environ['DJANGO_SETTINGS_MODULE'] = 'bowlero_backend.settings'
django.setup()

from bowlero_backend.settings import TIME_ZONE, BASE_DIR
from django.http import JsonResponse

from RM.Centers.models.models import *
from RM.Pricing.models.models import *
from RM.Food.models.models import *

from utils.UDatetime import UDatetime

EST = pytz.timezone(TIME_ZONE)


class ProductOptLoadProcessor:

    @classmethod
    def product_opt_load_processor(cls):

        centers = Centers.objects.all()
        centers_obj = pd.DataFrame.from_records(centers.values(
            'center_id',
            'weekday_prime',
            'weekend_premium',
            'monday_mayhem',
            'sunday_funday_bowling',
            'sunday_funday_shoes',
            'college_night_wed',
            'college_night_thu',
            'tuesday_222',
            'center_type'
        ))

        centers_record = pd.DataFrame.from_records(centers_obj)

        for index, row in centers_record.iterrows():
            center = Centers.objects.get(center_id=row['center_id'])
            center_type = row['center_type']

            #
            product_obj = Product.objects.get(product_id=107)
            ProductOpt.objects.update_or_create(
                product_id=product_obj,
                center_id=center,
                defaults={
                    'opt': 'In',
                }
            )
            product_obj = Product.objects.get(product_id=108)
            ProductOpt.objects.update_or_create(
                product_id=product_obj,
                center_id=center,
                defaults={
                    'opt': 'In',
                }
            )

            product_obj = Product.objects.get(product_id=111)
            ProductOpt.objects.update_or_create(
                product_id=product_obj,
                center_id=center,
                defaults={
                    'opt': 'In',
                }
            )

            if row['weekday_prime']:
                opt = row['weekday_prime']
                if opt == 'In':
                    opt_oppo = 'Out'
                else:
                    opt_oppo = 'In'

                product = Product.objects.get(product_id=110)
                ProductOpt.objects.update_or_create(
                    product_id=product,
                    center_id=center,
                    defaults={
                        'opt': opt,
                    }
                )
                product = Product.objects.get(product_id=109)
                ProductOpt.objects.update_or_create(
                    product_id=product,
                    center_id=center,
                    defaults={
                        'opt': opt_oppo,
                    }
                )
            if row['weekend_premium']:
                opt = row['weekend_premium']
                if opt == 'In':
                    opt_oppo = 'Out'
                else:
                    opt_oppo = 'In'

                product = Product.objects.get(product_id=113)
                ProductOpt.objects.update_or_create(
                    product_id=product,
                    center_id=center,
                    defaults={
                        'opt': opt,
                    }
                )
                product = Product.objects.get(product_id=112)
                ProductOpt.objects.update_or_create(
                    product_id=product,
                    center_id=center,
                    defaults={
                        'opt': opt_oppo,
                    }
                )

            # if row['weekday_prime']:
            #     if center_type == 'experiential':
            #         product_id = 102
            #     else:
            #         product_id = 105
            #     product = Product.objects.get(product_id=product_id)
            #     productopt_obj, exist = ProductOpt.objects.update_or_create(
            #         product_id=product,
            #         center_id=center,
            #         defaults={
            #             'opt': row['weekday_prime'],
            #         }
            #     )
            # if row['weekend_premium']:
            #     if center_type == 'experiential':
            #         product_id = 103
            #     else:
            #         product_id = 106
            #     product = Product.objects.get(product_id=product_id)
            #     productopt_obj, exist = ProductOpt.objects.update_or_create(
            #         product_id=product,
            #         center_id=center,
            #         defaults={
            #             'opt': row['weekend_premium'],
            #         }
            #     )

            # # monday_mayhem
            # opt = 'In' if not pd.isna(row['monday_mayhem']) else 'Out'
            # product = Product.objects.get(product_id=2020)
            # productopt_obj, exist = ProductOpt.objects.update_or_create(
            #     product_id=product,
            #     center_id=center,
            #     defaults={
            #         'opt': opt,
            #     }
            # )
            #
            # # sunday_funday_bowling
            # opt = 'In' if not pd.isna(row['sunday_funday_bowling']) else 'Out'
            # product = Product.objects.get(product_id=2010)
            # productopt_obj, exist = ProductOpt.objects.update_or_create(
            #     product_id=product,
            #     center_id=center,
            #     defaults={
            #         'opt': opt,
            #     }
            # )
            #
            # # sunday_funday_shoes
            # opt = 'In' if not pd.isna(row['sunday_funday_shoes']) else 'Out'
            # product = Product.objects.get(product_id=2011)
            # productopt_obj, exist = ProductOpt.objects.update_or_create(
            #     product_id=product,
            #     center_id=center,
            #     defaults={
            #         'opt': opt,
            #     }
            # )
            #
            # # college_night_wed
            # opt = 'In' if not pd.isna(row['college_night_wed']) else 'Out'
            # product = Product.objects.get(product_id=2040)
            # productopt_obj, exist = ProductOpt.objects.update_or_create(
            #     product_id=product,
            #     center_id=center,
            #     defaults={
            #         'opt': opt,
            #     }
            # )
            #
            # # college_night_thu
            # opt = 'In' if not pd.isna(row['college_night_thu']) else 'Out'
            # product = Product.objects.get(product_id=2041)
            # productopt_obj, exist = ProductOpt.objects.update_or_create(
            #     product_id=product,
            #     center_id=center,
            #     defaults={
            #         'opt': opt,
            #     }
            # )
            #
            # # tuesday_222
            # opt = 'In' if not pd.isna(row['tuesday_222']) else 'Out'
            # product = Product.objects.get(product_id=2030)
            # productopt_obj, exist = ProductOpt.objects.update_or_create(
            #     product_id=product,
            #     center_id=center,
            #     defaults={
            #         'opt': opt,
            #     }
            # )

    @classmethod
    def product_opt_load_processor2(cls):

        start = dt(2018, 1, 1)

        centers = Centers.objects.all()
        centers_obj = pd.DataFrame.from_records(centers.values(
            'center_id',
            'weekday_prime',
            'weekend_premium',
            'monday_mayhem',
            'sunday_funday_bowling',
            'sunday_funday_shoes',
            'college_night_wed',
            'college_night_thu',
            'tuesday_222',
            'center_type'
        ))

        centers_record = pd.DataFrame.from_records(centers_obj)

        for index, row in centers_record.iterrows():
            center = Centers.objects.get(center_id=row['center_id'])

            #
            product_obj = Product.objects.get(product_id=107)
            ProductOpt.objects.update_or_create(
                product_id=product_obj,
                center_id=center,
                start=start,
                end=None,
                defaults={
                    'opt': 'In',
                }
            )
            product_obj = Product.objects.get(product_id=108)
            ProductOpt.objects.update_or_create(
                product_id=product_obj,
                center_id=center,
                start=start,
                end=None,
                defaults={
                    'opt': 'In',
                }
            )

            product_obj = Product.objects.get(product_id=111)
            ProductOpt.objects.update_or_create(
                product_id=product_obj,
                center_id=center,
                start=start,
                end=None,
                defaults={
                    'opt': 'In',
                }
            )

            if row['weekday_prime']:
                opt = row['weekday_prime']
                if opt == 'In':
                    opt_oppo = 'Out'
                else:
                    opt_oppo = 'In'

                product = Product.objects.get(product_id=110)
                ProductOpt.objects.update_or_create(
                    product_id=product,
                    center_id=center,
                    start=start,
                    end=None,
                    defaults={
                        'opt': opt,
                    }
                )
                product = Product.objects.get(product_id=109)
                ProductOpt.objects.update_or_create(
                    product_id=product,
                    center_id=center,
                    start=start,
                    end=None,
                    defaults={
                        'opt': opt_oppo,
                    }
                )
            if row['weekend_premium']:
                opt = row['weekend_premium']
                if opt == 'In':
                    opt_oppo = 'Out'
                else:
                    opt_oppo = 'In'

                product = Product.objects.get(product_id=113)
                ProductOpt.objects.update_or_create(
                    product_id=product,
                    center_id=center,
                    start=start,
                    end=None,
                    defaults={
                        'opt': opt,
                    }
                )
                product = Product.objects.get(product_id=112)
                ProductOpt.objects.update_or_create(
                    product_id=product,
                    center_id=center,
                    start=start,
                    end=None,
                    defaults={
                        'opt': opt_oppo,
                    }
                )

            # monday_mayhem
            opt = 'In' if not pd.isna(row['monday_mayhem']) else 'Out'
            product = Product.objects.get(product_id=2020)
            ProductOpt.objects.update_or_create(
                product_id=product,
                center_id=center,
                start=start,
                end=None,
                defaults={
                    'opt': opt,
                }
            )

            # sunday_funday_bowling
            opt = 'In' if not pd.isna(row['sunday_funday_bowling']) else 'Out'
            product = Product.objects.get(product_id=2010)
            ProductOpt.objects.update_or_create(
                product_id=product,
                center_id=center,
                start=start,
                end=None,
                defaults={
                    'opt': opt,
                }
            )

            # sunday_funday_shoes
            opt = 'In' if not pd.isna(row['sunday_funday_shoes']) else 'Out'
            product = Product.objects.get(product_id=2011)
            ProductOpt.objects.update_or_create(
                product_id=product,
                center_id=center,
                start=start,
                end=None,
                defaults={
                    'opt': opt,
                }
            )

            # college_night_wed
            opt = 'In' if not pd.isna(row['college_night_wed']) else 'Out'
            product = Product.objects.get(product_id=2040)
            ProductOpt.objects.update_or_create(
                product_id=product,
                center_id=center,
                start=start,
                end=None,
                defaults={
                    'opt': opt,
                }
            )

            # college_night_thu
            opt = 'In' if not pd.isna(row['college_night_thu']) else 'Out'
            product = Product.objects.get(product_id=2041)
            ProductOpt.objects.update_or_create(
                product_id=product,
                center_id=center,
                start=start,
                end=None,
                defaults={
                    'opt': opt,
                }
            )

            # tuesday_222
            opt = 'In' if not pd.isna(row['tuesday_222']) else 'Out'
            product = Product.objects.get(product_id=2030)
            ProductOpt.objects.update_or_create(
                product_id=product,
                center_id=center,
                start=start,
                end=None,
                defaults={
                    'opt': opt,
                }
            )

    @classmethod
    def product_opt_migrate(cls):

        start = dt(2018, 1, 1)

        productopt_objs = ProductOpt.objects.exclude(action_user=None)

        for productopt_obj in productopt_objs:
            product_id = productopt_obj.product_id.product_id
            center_obj = productopt_obj.center_id
            opt = productopt_obj.opt
            username = productopt_obj.action_user
            tracking_id = productopt_obj.tracking_id

            if opt == 'In':
                opt_oppo = 'Out'
            else:
                opt_oppo = 'In'

            if product_id == '105':
                product_obj = Product.objects.get(product_id='110')
                ProductOpt.objects.update_or_create(
                    product_id=product_obj,
                    center_id=center_obj,
                    start=start,
                    end=None,
                    defaults={
                        'opt': opt,
                        'action_user': username,
                        'action_time': UDatetime.now_local(),
                        'tracking_id': tracking_id
                    }
                )
                product_obj_oppo = Product.objects.get(product_id='109')
                ProductOpt.objects.update_or_create(
                    product_id=product_obj_oppo,
                    center_id=center_obj,
                    start=start,
                    end=None,
                    defaults={
                        'opt': opt_oppo,
                        'action_user': username,
                        'action_time': UDatetime.now_local(),
                        'tracking_id': tracking_id
                    }
                )
            elif product_id == '106':
                product_obj = Product.objects.get(product_id='113')
                ProductOpt.objects.update_or_create(
                    product_id=product_obj,
                    center_id=center_obj,
                    start=start,
                    end=None,
                    defaults={
                        'opt': opt,
                        'action_user': username,
                        'action_time': UDatetime.now_local(),
                        'tracking_id': tracking_id
                    }
                )
                product_obj_oppo = Product.objects.get(product_id='112')
                ProductOpt.objects.update_or_create(
                    product_id=product_obj_oppo,
                    center_id=center_obj,
                    start=start,
                    end=None,
                    defaults={
                        'opt': opt_oppo,
                        'action_user': username,
                        'action_time': UDatetime.now_local(),
                        'tracking_id': tracking_id
                    }
                )

    @classmethod
    def product_opt_shoe(cls):

        start = dt(2018, 1, 1)
        center_objs = Centers.objects.filter(status='open')

        for center_obj in center_objs:

            product_obj_114 = Product.objects.get(product_id='114')
            ProductOpt.objects.update_or_create(
                product_id=product_obj_114,
                center_id=center_obj,
                start=start,
                end=None,
                defaults={
                    'opt': 'In',
                }
            )

            product_obj_115 = Product.objects.get(product_id='115')
            ProductOpt.objects.update_or_create(
                product_id=product_obj_115,
                center_id=center_obj,
                start=start,
                end=None,
                defaults={
                    'opt': 'In',
                }
            )



if __name__ == "__main__":
    # ProductOptLoadProcessor.product_opt_load_processor2()
    # ProductOptLoadProcessor.product_opt_migrate()
    ProductOptLoadProcessor.product_opt_shoe()
