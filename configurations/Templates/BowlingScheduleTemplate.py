from datetime import datetime, time, timedelta
from django.db.models import Q, Count, Min, Sum, Avg

import django
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'bowlero_backend.settings'
django.setup()

from RM.Centers.models.models import *
from RM.Pricing.models.models import *

def get_BowlingScheduleTemplate(weekday_prime='In', weekend_premium='In'):

    result = []

    if weekday_prime == 'In' and weekend_premium == 'In':
        result = [
            # weekday in
            {'DOW': 'mon', 'start': time(5), 'end': time(16), 'period_label': 'non-prime'},
            {'DOW': 'mon', 'start': time(16), 'end': time(20), 'period_label': 'prime'},
            {'DOW': 'mon', 'start': time(20), 'end': time(23, 59), 'period_label': 'non-prime'},
            {'DOW': 'tue', 'start': time(0), 'end': time(4), 'period_label': 'non-prime'},
            {'DOW': 'tue', 'start': time(5), 'end': time(16), 'period_label': 'non-prime'},
            {'DOW': 'tue', 'start': time(16), 'end': time(20), 'period_label': 'non-prime'},
            {'DOW': 'tue', 'start': time(20), 'end': time(23, 59), 'period_label': 'non-prime'},
            {'DOW': 'wed', 'start': time(0), 'end': time(4), 'period_label': 'non-prime'},
            {'DOW': 'wed', 'start': time(5), 'end': time(16), 'period_label': 'non-prime'},
            {'DOW': 'wed', 'start': time(16), 'end': time(20), 'period_label': 'non-prime'},
            {'DOW': 'wed', 'start': time(20), 'end': time(23, 59), 'period_label': 'non-prime'},
            {'DOW': 'thu', 'start': time(0), 'end': time(4), 'period_label': 'non-prime'},
            {'DOW': 'thu', 'start': time(5), 'end': time(16), 'period_label': 'non-prime'},
            {'DOW': 'thu', 'start': time(16), 'end': time(20), 'period_label': 'non-prime'},
            {'DOW': 'thu', 'start': time(20), 'end': time(23, 59), 'period_label': 'non-prime'},
            {'DOW': 'fri', 'start': time(0), 'end': time(4), 'period_label': 'non-prime'},
            # weekend in
            {'DOW': 'fri', 'start': time(5), 'end': time(16), 'period_label': 'non-prime'},
            {'DOW': 'fri', 'start': time(16), 'end': time(20), 'period_label': 'prime'},
            {'DOW': 'fri', 'start': time(20), 'end': time(23,59), 'period_label': 'premium'},
            {'DOW': 'sat', 'start': time(0), 'end': time(4), 'period_label': 'premium'},
            {'DOW': 'sat', 'start': time(5), 'end': time(20), 'period_label': 'prime'},
            {'DOW': 'sat', 'start': time(20), 'end': time(23, 59), 'period_label': 'premium'},
            {'DOW': 'sun', 'start': time(0), 'end': time(4), 'period_label': 'premium'},
            {'DOW': 'sun', 'start': time(5), 'end': time(18), 'period_label': 'prime'},
            {'DOW': 'sun', 'start': time(18), 'end': time(23,59), 'period_label': 'non-prime'},
            {'DOW': 'mon', 'start': time(0), 'end': time(4), 'period_label': 'non-prime'},
        ]
    elif weekday_prime == 'In' and weekend_premium == 'Out':
        result = [
            # weekday in
            {'DOW': 'mon', 'start': time(5), 'end': time(16), 'period_label': 'non-prime'},
            {'DOW': 'mon', 'start': time(16), 'end': time(20), 'period_label': 'prime'},
            {'DOW': 'mon', 'start': time(20), 'end': time(23, 59), 'period_label': 'non-prime'},
            {'DOW': 'tue', 'start': time(0), 'end': time(4), 'period_label': 'non-prime'},
            {'DOW': 'tue', 'start': time(5), 'end': time(16), 'period_label': 'non-prime'},
            {'DOW': 'tue', 'start': time(16), 'end': time(20), 'period_label': 'non-prime'},
            {'DOW': 'tue', 'start': time(20), 'end': time(23, 59), 'period_label': 'non-prime'},
            {'DOW': 'wed', 'start': time(0), 'end': time(4), 'period_label': 'non-prime'},
            {'DOW': 'wed', 'start': time(5), 'end': time(16), 'period_label': 'non-prime'},
            {'DOW': 'wed', 'start': time(16), 'end': time(20), 'period_label': 'non-prime'},
            {'DOW': 'wed', 'start': time(20), 'end': time(23, 59), 'period_label': 'non-prime'},
            {'DOW': 'thu', 'start': time(0), 'end': time(4), 'period_label': 'non-prime'},
            {'DOW': 'thu', 'start': time(5), 'end': time(16), 'period_label': 'non-prime'},
            {'DOW': 'thu', 'start': time(16), 'end': time(20), 'period_label': 'non-prime'},
            {'DOW': 'thu', 'start': time(20), 'end': time(23, 59), 'period_label': 'non-prime'},
            {'DOW': 'fri', 'start': time(0), 'end': time(4), 'period_label': 'non-prime'},
            # weekend out
            {'DOW': 'fri', 'start': time(5), 'end': time(16), 'period_label': 'non-prime'},
            {'DOW': 'fri', 'start': time(16), 'end': time(23, 59), 'period_label': 'prime'},
            {'DOW': 'sat', 'start': time(0), 'end': time(4), 'period_label': 'prime'},
            {'DOW': 'sat', 'start': time(5), 'end': time(23, 59), 'period_label': 'prime'},
            {'DOW': 'sun', 'start': time(0), 'end': time(4), 'period_label': 'prime'},
            {'DOW': 'sun', 'start': time(5), 'end': time(18), 'period_label': 'prime'},
            {'DOW': 'sat', 'start': time(18), 'end': time(23, 59), 'period_label': 'non-prime'},
            {'DOW': 'sat', 'start': time(0), 'end': time(4), 'period_label': 'non-prime'},
        ]
    elif weekday_prime == 'Out' and weekend_premium == 'In':
        result = [
            # weekday out
            {'DOW': 'mon', 'start': time(5), 'end': time(23, 59), 'period_label': 'non-prime'},
            {'DOW': 'tue', 'start': time(23, 59), 'end': time(4), 'period_label': 'non-prime'},
            {'DOW': 'tue', 'start': time(5), 'end': time(23, 59), 'period_label': 'non-prime'},
            {'DOW': 'wed', 'start': time(23, 59), 'end': time(4), 'period_label': 'non-prime'},
            {'DOW': 'wed', 'start': time(5), 'end': time(23, 59), 'period_label': 'non-prime'},
            {'DOW': 'thu', 'start': time(23, 59), 'end': time(4), 'period_label': 'non-prime'},
            {'DOW': 'thu', 'start': time(5), 'end': time(23, 59), 'period_label': 'non-prime'},
            {'DOW': 'fri', 'start': time(23, 59), 'end': time(4), 'period_label': 'non-prime'},
            # weekend in
            {'DOW': 'fri', 'start': time(5), 'end': time(16), 'period_label': 'non-prime'},
            {'DOW': 'fri', 'start': time(16), 'end': time(20), 'period_label': 'prime'},
            {'DOW': 'fri', 'start': time(20), 'end': time(23, 59), 'period_label': 'premium'},
            {'DOW': 'sat', 'start': time(0), 'end': time(4), 'period_label': 'premium'},
            {'DOW': 'sat', 'start': time(5), 'end': time(20), 'period_label': 'prime'},
            {'DOW': 'sat', 'start': time(20), 'end': time(23, 59), 'period_label': 'premium'},
            {'DOW': 'sun', 'start': time(0), 'end': time(4), 'period_label': 'premium'},
            {'DOW': 'sun', 'start': time(5), 'end': time(18), 'period_label': 'prime'},
            {'DOW': 'sun', 'start': time(18), 'end': time(23, 59), 'period_label': 'non-prime'},
            {'DOW': 'mon', 'start': time(0), 'end': time(4), 'period_label': 'non-prime'},
        ]
    elif weekday_prime == 'Out' and weekend_premium == 'Out':
        result = [
            # weekday out
            {'DOW': 'mon', 'start': time(5), 'end': time(23, 59), 'period_label': 'non-prime'},
            {'DOW': 'tue', 'start': time(23, 59), 'end': time(4), 'period_label': 'non-prime'},
            {'DOW': 'tue', 'start': time(5), 'end': time(23, 59), 'period_label': 'non-prime'},
            {'DOW': 'wed', 'start': time(23, 59), 'end': time(4), 'period_label': 'non-prime'},
            {'DOW': 'wed', 'start': time(5), 'end': time(23, 59), 'period_label': 'non-prime'},
            {'DOW': 'thu', 'start': time(23, 59), 'end': time(4), 'period_label': 'non-prime'},
            {'DOW': 'thu', 'start': time(5), 'end': time(23, 59), 'period_label': 'non-prime'},
            {'DOW': 'fri', 'start': time(23, 59), 'end': time(4), 'period_label': 'non-prime'},
            # weekend out
            {'DOW': 'fri', 'start': time(5), 'end': time(16), 'period_label': 'non-prime'},
            {'DOW': 'fri', 'start': time(16), 'end': time(23, 59), 'period_label': 'prime'},
            {'DOW': 'sat', 'start': time(0), 'end': time(4), 'period_label': 'prime'},
            {'DOW': 'sat', 'start': time(5), 'end': time(23, 59), 'period_label': 'prime'},
            {'DOW': 'sun', 'start': time(0), 'end': time(4), 'period_label': 'prime'},
            {'DOW': 'sun', 'start': time(5), 'end': time(18), 'period_label': 'prime'},
            {'DOW': 'sat', 'start': time(18), 'end': time(23, 59), 'period_label': 'non-prime'},
            {'DOW': 'sat', 'start': time(0), 'end': time(4), 'period_label': 'non-prime'},
        ]

    return result


def init_bowling_schedule():

    centers = Centers.objects\
        .exclude(
            Q(weekday_prime=None) |
            Q(weekend_premium=None) |
            Q(center_type=None)
    )

    for center in centers:
        center_id = center.center_id
        center_type = center.center_type
        weekday_prime = center.weekday_prime
        weekend_premium = center.weekend_premium

        schedules = get_BowlingScheduleTemplate(weekday_prime, weekend_premium)

        for schedule in schedules:
            period_label = schedule['period_label']

            if center_type == 'traditional' and period_label == 'non-prime':
                product = Product.objects.get(product_name='retail traditional non-prime bowling')
            elif center_type == 'traditional' and period_label == 'prime':
                product = Product.objects.get(product_name='retail traditional prime bowling')
            elif center_type == 'traditional' and period_label == 'premium':
                product = Product.objects.get(product_name='retail traditional premium bowling')
            elif center_type == 'experiential' and period_label == 'non-prime':
                product = Product.objects.get(product_name='retail experiential non-prime bowling')
            elif center_type == 'experiential' and period_label == 'prime':
                product = Product.objects.get(product_name='retail experiential prime bowling')
            elif center_type == 'experiential' and period_label == 'premium':
                product = Product.objects.get(product_name='retail experiential premium bowling')

            ProductWeeklySchedule.objects.update_or_create(
                DOW=schedule['DOW'],
                start_time=schedule['start'],
                end_time=schedule['end'],
                # perio
            )
        print(center_id, weekday_prime, weekend_premium)


if __name__ == '__main__':
    init_bowling_schedule()
