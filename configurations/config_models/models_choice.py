
DOW_choice = (
               ('mon', 'mon'),
               ('tue', 'tue'),
               ('wed', 'wed'),
               ('thu', 'thu'),
               ('fri', 'fri'),
               ('sat', 'sat'),
               ('sun', 'sun'),
             )

DOW_choice_map = {
                   'mon': 0,
                   'tue': 1,
                   'wed': 2,
                   'thu': 3,
                   'fri': 4,
                   'sat': 5,
                   'sun': 6,
                  }

DOW_weekday = ['mon', 'tue', 'wed', 'thu']
DOW_weekend = ['fri', 'sat', 'sun']

sell_type_choice = (
                     ('retail', 'retail'),
                     ('event', 'event'),
                   )

status_choice = (('active', 'active'),
                 ('inactive', 'inactive'),
                 )

bool_choice = (
               ('Y', 'Y'),
               ('N', 'N'),
              )


class CentersChoice:
    status_choice = (('open', 'open'),
                     ('closed', 'closed'),
                    )
    center_type_choice = (('traditional', 'traditional'),
                          ('experiential', 'experiential'),
                          ('session', 'session')
                         )


class PricingChoice:
    unit_type = (('by_unit', 'by_unit'),
                 ('by_time', 'by_time'),
                )


class PeriodChoice:
    period_label_choice = (('non-prime', 'non-prime'),
                           ('prime', 'prime'),
                           ('premium', 'premium'),
                          )


class ProductChoice:
    product_opt_choice = (('In', 'In'),
                          ('Out', 'Out'),
                         )

    product_status_choice = (('active', 'active'),
                             ('inactive', 'inactive'),
                            )

    products_always_opt_in = ['107', '108', '111', '114', '115']
    products_opt_oppo = ['110', '113']
    products_opt_oppo_dict = {'110': '109', '113': '112'}
    products_opt_oppo_pixel = ['2146571503', '2146436321']
    products_opt_oppo_dict_pixel = {'2146571503': '2146571501', '2146436321': '2146571502'}
    retail_bowling_ids_new_short = ['108', '110', '111', '113']
    retail_bowling_ids_new = ['108', '109', '110', '111', '112', '113']

    retail_bowling_ids = ['101', '102', '103', '104', '105', '106']
    retail_bowling_non_prime_product_ids = ['101', '104']
    retail_bowling_prime_product_ids = ['102', '105']
    retail_bowling_premium_product_ids = ['103', '106']
    retail_shoe_product_ids = ['107']
    retail_shoe_product_ids_new = ['114', '115']
    promo_product_ids = ['2010', '2011', '2020', '2030', '2040', '2041']

    retail_bowling_traditional_center = ['104', '105', '106']
    retail_bowling_experiential_center = ['101', '102', '103']
    retail_bowling_session_center = ['104', '105', '106']

    retail_bowling_map = {
        'non-prime': {'experiential': '101', 'traditional': '104'},
        'prime': {'experiential': '102', 'traditional': '105'},
        'premium': {'experiential': '103', 'traditional': '106'}
    }

    event_bowling_product_ids = ['3001', '3002', '3003', '3004', '3005', '3006', '3007']
    event_bowling_product_tuple = [('3001', 'Lane M-Tu <5pm (2.5h)'),
                                   ('3002', 'Lane M-Tu >5pm (2.5h)'),
                                   ('3003', 'Lane W-Th <5pm (2.5h)'),
                                   ('3004', 'Lane W-Th >5pm (2.5h)'),
                                   ('3005', 'Lane F-Sa (2.5h)'),
                                   ('3006', 'Lane Su <5pm (2.5h)'),
                                   ('3007', 'Lane Su >5pm (2.5h)')]
    event_basic_packages_product_tuple = [('3201', 'Kids Unbelieva'),
                                   ('3202', 'Kids Unstoppa'),
                                   ('3203', 'Kids Remarka'),
                                   ('3204', 'Parent Plate Unbelieva'),
                                   ('3205', 'Parent Plate Unstoppa'),
                                   ('3206', 'Parent Plate Remarka'),
                                   ('3207', 'Pampered Parent Unbelieva'),
                                   ('3208', 'Pampered Parent Unstoppa'),
                                   ('3209', 'Pampered Parent Remarka')]
    event_shoe_product_ids = ['3101']
    event_basic_packages_product_ids = ['3201', '3202', '3203', '3204', '3205', '3206', '3207', '3208', '3209']

    # session_centers = ['34', '87', '238', '305', '357', '362', '564', '621', '893']


class ProductScheduleChoice:
    freq_choice = (('Once', 'Once'),
                   ('Anually', 'Anually'),
                   ('Weekly', 'Weekly'),
                   ('Daily', 'Daily'),
                   )

