import datetime as dt
import time
import calendar
import pytz
from datetime import datetime, timedelta
from dateutil import tz
from dateutil.parser import parse
from tzlocal import get_localzone

from configurations.config_models.models_choice import *


class UDatetime:

    local_tz = get_localzone()

    def __init__(self):
        pass

    @classmethod
    def now_local(cls):
        return cls.local_tz.localize(datetime.now())

    @classmethod
    def localize(cls, date):
        return cls.local_tz.localize(date)

    @classmethod
    def to_local(cls, date):
        return date.astimezone(tz=cls.local_tz)

    @classmethod
    def datetime_str_init(cls, timestamp,
                          default_base=None,
                          default_delta=timedelta(days=0),
                          empty_default=True
                          ):
        if timestamp:
            timestamp = parse(timestamp)
            if not timestamp.tzinfo:
                timestamp = cls.local_tz.localize(timestamp)
        else:
            if empty_default:
                if not default_base:
                    default_base = cls.now_local()
                timestamp = default_base + default_delta
            else:
                timestamp = None

        return timestamp

    @classmethod
    def pick_date_by_one_date(cls, date):
        ahead = date - cls.local_tz.localize(datetime(date.year, date.month, date.day))
        behind = cls.local_tz.localize(datetime(date.year, date.month, date.day) + timedelta(days=1)) - date
        if ahead.total_seconds() >= behind.total_seconds() and behind.total_seconds() <= (3600*6):
            picked_date = (date + timedelta(days=1)).date()
        elif ahead.total_seconds() < behind.total_seconds() and ahead.total_seconds() <= (3600*6):
            picked_date = (date - timedelta(days=1)).date()
        else:
            picked_date = date.date()
        return picked_date

    @classmethod
    def pick_date_by_two_date(cls, start, end):
        if start.date() == end.date():
            return start.date()
        elif start.date() + timedelta(days=1) == end.date():
            middle = cls.local_tz.localize(datetime(start.year, start.month, start.day+1))
            ahead = middle - start
            behind = end - middle
            if behind >= ahead:
                return end.date()
            else:
                return start.date()
        else:
            return start.date() + timedelta(days=1)

    @classmethod
    def get_overlap(cls, r1_start, r1_end, r2_start, r2_end):

        r1_start = r1_start.astimezone(cls.local_tz)
        r1_end = r1_end.astimezone(cls.local_tz)
        r2_start = r2_start.astimezone(cls.local_tz)
        r2_end = r2_end.astimezone(cls.local_tz)

        latest_start = max(r1_start, r2_start)
        earliest_end = min(r1_end, r2_end)

        delta = earliest_end - latest_start

        if delta.total_seconds() > 0:
            return delta
        else:
            return timedelta(hours=0)

    @classmethod
    def check_date_format(cls, date_str):
        try:
            datetime.strptime(date_str, '%Y/%m/%d')
            return 'YY/mm/dd'
        except Exception as e:
            pass

        try:
            datetime.strptime(date_str, '%m/%d/%Y')
            return 'mm/dd/YY'
        except Exception as e:
            pass

        return None

    @classmethod
    def date_range(cls, start, end, DOW=None):
        r = (end + timedelta(days=1) - start).days
        date_range = [start + timedelta(days=i) for i in range(r)]
        if DOW:
            date_range_temp = []
            for date in date_range:
                if DOW_choice[date.weekday()][0] in DOW:
                    date_range_temp += [date]

            date_range = date_range_temp

        return date_range

    @classmethod
    def week_range(cls, date):

        weekday = date.weekday()

        start = date - timedelta(days=weekday)
        end = start + timedelta(days=6)

        date_range = cls.date_range(start, end)

        return date_range

    @classmethod
    def date_range_by_DOW(cls, DOW, date=None, week_len=4):

        if not date:
            date = UDatetime.now_local().date()
        weekday = date.weekday()
        base = date - timedelta(days=weekday) + timedelta(days=DOW_choice_map[DOW])

        date_range = [base + timedelta(days=7*i) for i in range(week_len)]

        return date_range



