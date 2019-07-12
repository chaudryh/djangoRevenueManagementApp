import numpy as np
import pandas as pd
import time
import pytz
import ast
import itertools
import re
import calendar
from babel.numbers import format_decimal, format_currency

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

freqMap = {
    'Once Every Other Week': 1,
    'Once Every Week': 2,
    'Once Every 4 weeks': 3,
    '1st week of the month': 4,
    '3rd week of the month': 5,
    '2nd week of the month': 6,
    '2nd & 4th week of the month': 7,
    '4th week of the month': 8,
    '1st & 3rd week of the month': 9,
}

dow_map = {'1': 'Monday', '2': 'Tuesday', '3': 'Wednesday', '4': 'Thursday',
           '5': 'Friday', '6': 'Saturday', '7': 'Sunday'}

dow_map_reverse = {'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4,
                   'Friday': 5, 'Saturday': 6, 'Sunday': 7}


def week_of_month(dt):
    mth = calendar.monthcalendar(dt.year, dt.month)
    for i, wk in enumerate(mth):
        if dt.day in wk:
            return i + 1


def days_in_range(start, end, dow):

    if (end - start).days < 0:
        res = 0
    elif start == end:
        res = 1 if (start.weekday() + 1) in dow else 0
    elif 0 < (end - start).days < 7:
        start_dow = start.weekday() + 1
        end_dow = end.weekday() + 1
        if start_dow <= end_dow:
            res = len(set(range(start_dow, end_dow + 1)) & dow)
        else:
            res = 0
            res += len(set(range(start_dow, 8)) & dow)
            res += len(set(range(1, end_dow + 1)) & dow)
    else:
        res = 0
        start_dow = start.weekday() + 1
        end_dow = end.weekday() + 1
        res += len(set(range(start_dow, 8)) & dow)
        res += len(set(range(1, end_dow + 1)) & dow)

        mid_weeks_start = start + td(days=7 - start_dow)
        mid_weeeks_end = end - td(days=end_dow)
        res += (mid_weeeks_end - mid_weeks_start).days // 7 * len(dow)

    return res


class LeagueDataDao:
    @classmethod
    def get_league_pricing_sheet(cls, duration,
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
            .filter(status='open') \
            .extra(select={'center_id': 'CAST(center_id AS INTEGER)'}) \
            .order_by(sort)

        leagues = LeaguePricingSheet.objects.all()
        leagueFilter = False
        if duration:
            leagues = leagues.filter(duration=duration)

        if filters:
            filters = ast.literal_eval(filters)

            for key, value in filters.items():
                filters_list = value.split(',')
                filters_list = [x.strip() for x in filters_list]
                filters[key] = filters_list

            # Filter for center fields
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

            # Filter for League Pricing Sheet
            if filters.get('bowleroM'):
                filter_item = filters.get('bowleroM')
                if len(filter_item) == 1:
                    leagues = leagues.filter(bowleroM__icontains=filter_item[0])
                else:
                    leagues = leagues.filter(reduce(operator.or_, (Q(bowleroM__icontains=item)
                                                                   for item in filter_item if item)))
            if filters.get('min_lineage_fee_bowlero'):
                leagueFilter = True
                filter_item = filters.get('min_lineage_fee_bowlero')
                if len(filter_item) == 1:
                    leagues = leagues.filter(min_lineage_fee_bowlero__icontains=filter_item[0])
                else:
                    leagues = leagues.filter(reduce(operator.or_, (Q(min_lineage_fee_bowlero__icontains=item)
                                                                   for item in filter_item if item)))
            if filters.get('max_lineage_fee_bowlero'):
                leagueFilter = True
                filter_item = filters.get('max_lineage_fee_bowlero')
                if len(filter_item) == 1:
                    leagues = leagues.filter(max_lineage_fee_bowlero__icontains=filter_item[0])
                else:
                    leagues = leagues.filter(reduce(operator.or_, (Q(max_lineage_fee_bowlero__icontains=item)
                                                                   for item in filter_item if item)))
            if filters.get('max_cover'):
                leagueFilter = True
                filter_item = filters.get('max_cover')
                if len(filter_item) == 1:
                    leagues = leagues.filter(max_cover__icontains=filter_item[0])
                else:
                    leagues = leagues.filter(reduce(operator.or_, (Q(max_cover__icontains=item)
                                                                   for item in filter_item if item)))
            if filters.get('cost_of_acquisition'):
                leagueFilter = True
                filter_item = filters.get('cost_of_acquisition')
                if len(filter_item) == 1:
                    leagues = leagues.filter(cost_of_acquisition__icontains=filter_item[0])
                else:
                    leagues = leagues.filter(reduce(operator.or_, (Q(cost_of_acquisition__icontains=item)
                                                                   for item in filter_item if item)))
            if filters.get('cost_of_retention'):
                leagueFilter = True
                filter_item = filters.get('cost_of_retention')
                if len(filter_item) == 1:
                    leagues = leagues.filter(cost_of_retention__icontains=filter_item[0])
                else:
                    leagues = leagues.filter(reduce(operator.or_, (Q(cost_of_retention__icontains=item)
                                                                   for item in filter_item if item)))
            if filters.get('max_ceiling_customer_fund'):
                leagueFilter = True
                filter_item = filters.get('max_ceiling_customer_fund')
                if len(filter_item) == 1:
                    leagues = leagues.filter(max_ceiling_customer_fund__icontains=filter_item[0])
                else:
                    leagues = leagues.filter(reduce(operator.or_, (Q(max_ceiling_customer_fund__icontains=item)
                                                                   for item in filter_item if item)))
            if filters.get('actualPF'):
                leagueFilter = True
                filter_item = filters.get('actualPF')
                if len(filter_item) == 1:
                    leagues = leagues.filter(actualPF__icontains=filter_item[0])
                else:
                    leagues = leagues.filter(reduce(operator.or_, (Q(actualPF__icontains=item)
                                                                   for item in filter_item if item)))
            if filters.get('share_of_PF_bowlero'):
                leagueFilter = True
                filter_item = filters.get('share_of_PF_bowlero')
                if len(filter_item) == 1:
                    leagues = leagues.filter(share_of_PF_bowlero__icontains=filter_item[0])
                else:
                    leagues = leagues.filter(reduce(operator.or_, (Q(share_of_PF_bowlero__icontains=item)
                                                                   for item in filter_item if item)))
            if filters.get('share_of_PF_treasurer'):
                leagueFilter = True
                filter_item = filters.get('share_of_PF_treasurer')
                if len(filter_item) == 1:
                    leagues = leagues.filter(share_of_PF_treasurer__icontains=filter_item[0])
                else:
                    leagues = leagues.filter(reduce(operator.or_, (Q(share_of_PF_treasurer__icontains=item)
                                                                   for item in filter_item if item)))

        # Filter Common centers
        centers_list_centers = centers.values_list('center_id', flat=True).distinct()
        centers_list_leagues = leagues.values_list('center_id', flat=True).distinct()
        if centers_list_leagues and leagueFilter:
            centers_list_leagues = list(map(int, centers_list_leagues))
            centers_list_common = list(set(centers_list_centers) & set(centers_list_leagues))
        else:
            centers_list_common = centers_list_centers

        if not centers_list_common:
            return pd.DataFrame(), 0
        centers = centers.filter(center_id__in=centers_list_common)
        leagues = leagues.filter(center_id__in=centers_list_common)

        num = centers.count()

        if pagination:
            paginator = Paginator(centers, page_size, )
            current_page = int(offset / page_size) + 1
            centers = paginator.page(current_page).object_list

        centers_record = pd.DataFrame.from_records(centers.values(
            'center_id',
            'center_name',
            'region',
            'district',
        ))

        leagues_record = pd.DataFrame.from_records(leagues.values(
            'center_id',
            'bowleroM',
            'min_lineage_fee_bowlero',
            'max_lineage_fee_bowlero',
            'max_cover',
            'cost_of_acquisition',
            'cost_of_retention',
            'max_ceiling_customer_fund',
            'actualPF',
            'share_of_PF_bowlero',
            'share_of_PF_treasurer',
        ))

        if centers_record.empty:
            return pd.DataFrame(), 0
        leagues_record = leagues_record.where((pd.notnull(leagues_record)), None)

        if not leagues_record.empty:
            leagues_record['center_id'] = leagues_record['center_id'].apply(str)
            centers_record['center_id'] = centers_record['center_id'].apply(str)

            centers_record = centers_record.join(leagues_record.set_index(['center_id']), on=['center_id'], how='left')
            centers_record = centers_record.where((pd.notnull(centers_record)), None)

            # Monetarize
            moneyFields = ['min_lineage_fee_bowlero', 'max_lineage_fee_bowlero', 'cost_of_acquisition',
                           'cost_of_retention', 'max_ceiling_customer_fund', 'actualPF']
            for field in moneyFields:
                centers_record[field] = centers_record[field].apply(lambda x: str(int(x)) if x and x % 1 == 0 else x)
                centers_record[field] = centers_record[field].apply(lambda x: '${price}'.format(price=x) if x else None)

            # Percentile
            percFields = ['share_of_PF_bowlero', 'share_of_PF_treasurer']
        else:
            columns = ['min_lineage_fee_bowlero', 'max_lineage_fee_bowlero', 'max_cover', 'cost_of_acquisition',
                       'cost_of_retention', 'max_ceiling_customer_fund',
                       'actualPF', 'share_of_PF_bowlero', 'share_of_PF_treasurer']
            for column in columns:
                if column not in centers_record.columns:
                    centers_record[column] = None

        return centers_record, num

    @classmethod
    def get_center_info(cls, start, end, type_, subType, dow, dowRange, dateRange, status, distinct,
                        pagination=False, page_size=None, offset=None, filters=None, sort=None, order=None):

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
                    centers = centers.filter(reduce(operator.or_, (Q(center_name__icontains=item) for item in filter_item if item)))
            if filters.get('region'):
                filter_item = filters.get('region')
                if len(filter_item) == 1:
                    centers = centers.filter(region__icontains=filter_item[0])
                else:
                    centers = centers.filter(reduce(operator.or_, (Q(region__icontains=item) for item in filter_item if item)))
            if filters.get('district'):
                filter_item = filters.get('district')
                if len(filter_item) == 1:
                    centers = centers.filter(district__icontains=filter_item[0])
                else:
                    centers = centers.filter(reduce(operator.or_, (Q(district__icontains=item) for item in filter_item if item)))

        num = centers.count()

        if pagination:
            paginator = Paginator(centers, page_size,)
            current_page = int(offset/page_size) + 1
            centers = paginator.page(current_page).object_list

        centers_id_list = centers.values_list('center_id', flat=True)

        centers_record = pd.DataFrame.from_records(centers.values(
                                                           'center_id',
                                                           'center_name',
                                                           'region',
                                                           'district',
                                                           ))

        if centers_record.empty:

            return pd.DataFrame(), 0

        # Start to calculate league statistics
        # Filter data
        leagueObjs = League.objects.filter(centerId__in=centers_id_list).exclude(confirmedBowlerCount__lt=8)
        if dateRange == 'intersection':
            if start:
                leagueObjs = leagueObjs.exclude(end__lt=start)
            if end:
                leagueObjs = leagueObjs.exclude(start__gt=end)
        elif dateRange == 'specific':
            if start:
                leagueObjs = leagueObjs.filter(start__gte=start)
            if end:
                leagueObjs = leagueObjs.filter(end__lte=end)
        elif dateRange == 'ended':
            if start:
                leagueObjs = leagueObjs.exclude(end__lt=start)
            if end:
                leagueObjs = leagueObjs.exclude(start__gt=end).filter(end__lte=end)

        if type_:
            leagueObjs = leagueObjs.filter(reduce(operator.or_, (Q(leagueType__contains=i) for i in type_)))
        if subType:
            leagueObjs = leagueObjs.filter(reduce(operator.or_, (Q(leagueSubType__contains=i) for i in subType)))
        if status:
            leagueObjs = leagueObjs.filter(reduce(operator.or_, (Q(leagueStatus__contains=i) for i in status)))
        if dow:
            leagueObjs = leagueObjs.filter(reduce(operator.or_, (Q(dayOfWeekName__contains=dow_map[i]) for i in dow)))
        if distinct:
            leagueObjs = leagueObjs.filter(last=True)

        leagueRecords = pd.DataFrame.from_records(leagueObjs.values('centerId',
                                                                    'leagueId',
                                                                    'start',
                                                                    'end',
                                                                    'dayOfWeekName',
                                                                    'daysPerWeek',
                                                                    'numberOfWeeks',
                                                                    'startingLaneNumber',
                                                                    'endingLaneNumber',
                                                                    'bowlerEquivalentGoal',
                                                                    'confirmedBowlerCount',
                                                                    'playersPerTeam',
                                                                    'numberOfTeams',
                                                                    'gamesPerPlayer',
                                                                    'lineageCost',
                                                                    'leagueFrequency',
                                                                    ))

        if leagueRecords.empty:
            return centers_record, num

        dow_ = [dow_map[i] for i in dow]
        # Add columns
        leagueRecords['start'] = leagueRecords['start'].dt.date
        leagueRecords['end'] = leagueRecords['end'].dt.date
        if dowRange == 'specific':
            leagueRecords['daysPerWeek'] = leagueRecords['dayOfWeekName'].apply(lambda x: len(set(x.split(',')) & set(dow_)))
        leagueRecords['sumGames'] = leagueRecords['bowlerEquivalentGoal'] * leagueRecords['gamesPerPlayer']
        leagueRecords['weeklyValue'] = (leagueRecords['daysPerWeek'] * leagueRecords['lineageCost'] * leagueRecords['bowlerEquivalentGoal']).round(0)
        leagueRecords['seasonalValue'] = (leagueRecords['weeklyValue'] * leagueRecords['numberOfWeeks']).round(0)

        # Calculate Revenue
        leagueRecords['leagueFrequency_'] = leagueRecords['leagueFrequency'].apply(lambda x: freqMap[x] if x else 2)
        leagueRecords['revPerDay'] = leagueRecords['lineageCost'] * leagueRecords['bowlerEquivalentGoal']
        leagueRecords['revDOW'] = leagueRecords['dayOfWeekName'] \
            .apply(lambda x: list(set(x.split(',')) & set(dow_)) if dow_ else x.split(','))

        # minWeeks Min week = min(NumberOfWeeks) = min(36,12,10)=10
        # maxWeeks Max week = max(NumberOfWeeks) = max(36,12,10)=36
        # avgPlayersPerTeam Avg Players/Team = sum(confirmed)/sum(team) = (40+30+16)/(10+8+6)=3.58
        # avgPlayersPerLeague Avg Players/League = sum(confirmed)/count(league) = (40+30+16)/3=28.7
        # avgTeamsPerLeague Avg Teams/League = sum(team)/count(league) = (10+8+6)/3=8
        # avgGamesPerBowler Avg Games/Bowler = sum(confirmed * GamesPerPlayer)/sum(confirmed) = (40*5+30*4+16*3)/(40+30+16)=4.28
        # avgGamesPerLeague Avg Games/League = sum(confirmed * GamesPerPlayer)/count(league) = (40*5+30*4+16*3)/3=122.7
        # avgLineagePerLeague Avg Lineage$/League = sum(LineageCost)/count(league) = (10+12+13)/3=11.7
        # avgLineagePerGame Avg Lineage$/Game = sum(LineageCost)/sum(GamesPerPlayer) = (10+12+13)/(5+4+3)=2.9
        # avgLineagePerBowler Avg Lineage$/Bowler = sum(LineageCost*confirmed)/sum(confirmed) = (10*40+12*30+13*16)/(40+30+16)=11.3
        # weeklyValue Weekly Value (By Center) = sum(DaysPerWeek * LineageCost * confirmed) = 3*10*40+1*12*30+2*13*16 = $1976
        # avgWeeklyValue seasonalValue Avg Weekly Value = sum(DaysPerWeek * LineageCost * confirmed)/count(league) = (3*10*40+1*12*30+2*13*16)/3 = $658.7
        # seasonalValue Seasonal Value (By Center) = sum(NumberOfWeeks * DaysPerWeek * LineageCost * confirmed) = 36*3*10*40+12*1*12*30+10*2*13*16 = $51680
        # avgSeasonalValue Avg Seasonal Value = sum(NumberOfWeeks * DaysPerWeek * LineageCost * confirmed)/count(league) = (36*3*10*40+12*1*12*30+10*2*13*16)/3 = $17226.7

        # Aggregate Data
        def agg(x):
            revenue = 0
            revenue += x[x['leagueFrequency_'] == 2]['revenue'].round(0).sum()

            for index, row in x[x['leagueFrequency_'] != 2].iterrows():
                dates = pd.DataFrame(pd.date_range(row['start_'], row['end_']), columns=['date'])
                dates['value'] = 0
                dates['wom'] = dates['date'].apply(lambda x: week_of_month(x))
                dates['woy'] = dates['date'].apply(lambda x: x.isocalendar()[1])
                dates['dow'] = dates['date'].apply(lambda x: x.weekday() + 1)
                start_dow = dates.at[0, 'dow']

                if row['leagueFrequency_'] == 1:
                    dates = dates[abs(dates['woy'] - start_dow) % 2 == 0]
                    x.at[index, 'weeklyValue'] = x.at[index, 'weeklyValue'] / 2
                elif row['leagueFrequency_'] == 2:
                    pass
                elif row['leagueFrequency_'] == 3:
                    dates = dates[abs(dates['woy'] - start_dow) % 4 == 0]
                    x.at[index, 'weeklyValue'] = x.at[index, 'weeklyValue'] / 4
                elif row['leagueFrequency_'] == 4:
                    dates = dates[dates['wom'].isin([1])]
                    x.at[index, 'weeklyValue'] = x.at[index, 'weeklyValue'] / 4
                elif row['leagueFrequency_'] == 5:
                    dates = dates[dates['wom'].isin([3])]
                    x.at[index, 'weeklyValue'] = x.at[index, 'weeklyValue'] / 4
                elif row['leagueFrequency_'] == 6:
                    dates = dates[dates['wom'].isin([2])]
                    x.at[index, 'weeklyValue'] = x.at[index, 'weeklyValue'] / 4
                elif row['leagueFrequency_'] == 7:
                    dates = dates[dates['wom'].isin([2, 4])]
                    x.at[index, 'weeklyValue'] = x.at[index, 'weeklyValue'] / 2
                elif row['leagueFrequency_'] == 8:
                    dates = dates[dates['wom'].isin([4])]
                    x.at[index, 'weeklyValue'] = x.at[index, 'weeklyValue'] / 4
                elif row['leagueFrequency_'] == 9:
                    dates = dates[dates['wom'].isin([1, 3])]
                    x.at[index, 'weeklyValue'] = x.at[index, 'weeklyValue'] / 2

                # Filter by revDOW
                revDOW = [dow_map_reverse[i] for i in row['revDOW']]
                dates = dates[dates['dow'].isin(revDOW)]

                revenue += round(len(dates) * row['revPerDay'], 0)

            count = len(x)
            sumConfirmedBowlerCount = x['bowlerEquivalentGoal'].sum()
            sumNumberOfTeams = x['numberOfTeams'].sum()
            sumGames = (x['sumGames']).sum()
            sumLineageCost = x['lineageCost'].sum()
            SumWeeklyValue = x['weeklyValue'].sum()
            SumSeasonalValue = x['seasonalValue'].sum()

            res = pd.Series(
                {
                    'minWeeks': min(x['numberOfWeeks']),
                    'maxWeeks': max(x['numberOfWeeks']),
                    'avgPlayersPerTeam': round(sumConfirmedBowlerCount / sumNumberOfTeams, 2) if start != end else None,
                    'avgPlayersPerLeague': round(sumConfirmedBowlerCount / count, 2) if start != end else None,
                    'avgTeamsPerLeague': round(sumNumberOfTeams / count, 2) if start != end else None,
                    'avgGamesPerBowler': round(sumGames / sumConfirmedBowlerCount, 2) if start != end else None,
                    'avgGamesPerLeague': round(sumGames / count, 2) if start != end else None,
                    'avgLineagePerLeague': round(sumLineageCost / count, 2) if start != end else None,
                    'avgLineagePerGame': round(sumLineageCost / x['gamesPerPlayer'].sum(), 2) if start != end else None,
                    'avgLineagePerBowler': round(sumLineageCost / sumConfirmedBowlerCount, 2) if start != end else None,
                    'confirmedBowler': round(sumConfirmedBowlerCount, 0) if start != end else None,
                    # 'projectedBowler': round((x['playersPerTeam'] * x['numberOfTeams']).sum(), 0),
                    'weeklyValue': SumWeeklyValue,
                    'avgWeeklyValue': round(SumWeeklyValue / count, 0) if start != end else None,
                    'seasonalValue': SumSeasonalValue,
                    'avgSeasonalValue': round(SumSeasonalValue / count, 0) if start != end else None,
                    'revenue': round(revenue, 0) if revenue > 0 else None,
                    'leagueCount': count
                }
            )

            # res = pd.Series(
            #     {
            #         'minWeeks': min(x['numberOfWeeks']),
            #         'maxWeeks': max(x['numberOfWeeks']),
            #         'avgPlayersPerTeam': round(x['confirmedBowlerCount'].sum() / x['numberOfTeams'].sum(), 2),
            #         'avgPlayersPerLeague': round(x['confirmedBowlerCount'].sum() / len(x), 2),
            #         'avgTeamsPerLeague': round(x['numberOfTeams'].sum() / len(x), 2),
            #         'avgGamesPerBowler': round((x['confirmedBowlerCount'] * x['gamesPerPlayer']).sum() / x['confirmedBowlerCount'].sum(), 2),
            #         'avgGamesPerLeague': round((x['confirmedBowlerCount'] * x['gamesPerPlayer']).sum() / len(x), 2),
            #         'avgLineagePerLeague': round(x['lineageCost'].sum() / len(x), 2),
            #         'avgLineagePerGame': round(x['lineageCost'].sum() / x['gamesPerPlayer'].sum(), 2),
            #         'avgLineagePerBowler': round(x['lineageCost'].sum() / x['confirmedBowlerCount'].sum(), 2),
            #         'confirmedBowler': round(x['confirmedBowlerCount'].sum(), 0),
            #         # 'projectedBowler': round((x['playersPerTeam'] * x['numberOfTeams']).sum(), 0),
            #         'weeklyValue': round((x['daysPerWeek'] * x['lineageCost'] * x['confirmedBowlerCount']).sum(), 0),
            #         'projectedWeeklyValue': round((x['daysPerWeek'] * x['lineageCost'] * x['playersPerTeam'] * x['numberOfTeams']).sum(), 0),
            #         'avgWeeklyValue': round((x['daysPerWeek'] * x['lineageCost'] * x['confirmedBowlerCount']).sum() / len(x), 0),
            #         'seasonalValue': round((x['daysPerWeek'] * x['lineageCost'] * x['confirmedBowlerCount'] * x['numberOfWeeks']).sum(), 0),
            #         'avgSeasonalValue': round(((x['daysPerWeek'] * x['lineageCost'] * x['confirmedBowlerCount'] * x['numberOfWeeks'])).sum() / len(x), 0),
            #         'revenue': round(revenue, 0) if revenue > 0 else None,
            #     }
            # )

            return res

        leagueRecords['start_'] = leagueRecords['start'].apply(lambda x: max(x, start))
        leagueRecords['end_'] = leagueRecords['end'].apply(lambda x: min(x, end))
        leagueRecords['revDOW_'] = leagueRecords['revDOW'].apply(lambda x: set([dow_map_reverse[i] for i in x]))
        leagueRecords['days'] = leagueRecords[['start_', 'end_', 'revDOW_']] \
            .apply(lambda x: days_in_range(x['start_'], x['end_'], x['revDOW_']), axis=1)
        leagueRecords = leagueRecords[leagueRecords['days'] != 0]
        leagueRecords['revenue'] = leagueRecords['days'] * leagueRecords['revPerDay']

        leagueRecordsAgg = pd.DataFrame(leagueRecords.groupby(['centerId'])
                                                     .apply(agg),
                                        columns=[
                                            'minWeeks',
                                            'maxWeeks',
                                            'avgPlayersPerTeam',
                                            'avgPlayersPerLeague',
                                            'avgTeamsPerLeague',
                                            'avgGamesPerBowler',
                                            'avgGamesPerLeague',
                                            'avgLineagePerLeague',
                                            'avgLineagePerGame',
                                            'avgLineagePerBowler',
                                            'confirmedBowler',
                                            # 'projectedBowler',
                                            'weeklyValue',
                                            'avgWeeklyValue',
                                            'projectedWeeklyValue',
                                            'seasonalValue',
                                            'avgSeasonalValue',
                                            'revenue',
                                            'leagueCount'
                                            ]
                                        )

        leagueRecordsAgg.reset_index(inplace=True)

        # leagueRecordsAgg.rename({'centerId': 'center_id'}, axis=1, inplace=True)

        # if leagueRecords.empty:
        #     columns = ['min_weeks', 'max_weeks', 'cover_dow', 'cover_month', 'max_cover', 'avg_lineage_cost']
        #     for column in columns:
        #         if column not in centers_record.columns:
        #             centers_record[column] = None
        #     return centers_record, num

        # leagueRecords['duration'] = round((leagueRecords['end'] - leagueRecords['start']).dt.days/7, 2)

        # Costum Function

        #
        # def coverDOW(x):
        #     x = list(set(x.tolist()))
        #     x.sort()
        #     x = map(lambda i: dow_map[i], x)
        #     return ','.join(list(x))
        #
        # month_map = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug',
        #              9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
        #
        # def coverMonth(x):
        #     x = x.tolist()
        #     x = list(map(lambda i: i.split(' '), x))
        #     all_ = []
        #     for i in x:
        #         all_ += i
        #     all_ = list(set(all_))
        #     all_ = list(map(int, all_))
        #     all_.sort()
        #     all_ = map(lambda i: month_map[i], all_)
        #     return ','.join(all_)
        #
        # def getMonth(x):
        #     start_month, start_year = x['start'].month, x['start'].year
        #     end_month, end_year = x['end'].month, x['end'].year
        #     if start_year == end_year:
        #         months = list(range(start_month, end_month + 1))
        #     else:
        #         months = list(range(start_month, 13)) + list(range(1, end_month + 1))
        #     months = map(str, months)
        #
        #     return ' '.join(months)
        #
        # # Agg
        # leagueRecords['months'] = leagueRecords[['start', 'end']].apply(getMonth, axis=1)
        # leagueRecordsAgg = leagueRecords.groupby('center_id').agg({'duration': ['min', 'max'],
        #                                                            'dow': [coverDOW],
        #                                                            'months': [coverMonth],
        #                                                            'cover': ['max'],
        #                                                            'lineage_cost': ['mean'],
        #                                                            })
        #
        # leagueRecordsAgg.columns = ['min_weeks', 'max_weeks', 'cover_dow',
        #                             'cover_month', 'max_cover', 'avg_lineage_cost']
        # leagueRecordsAgg.reset_index(inplace=True)

        # Left join league stats to center table
        leagueRecordsAgg['centerId'] = leagueRecordsAgg['centerId'].apply(int)
        centers_record = centers_record.join(leagueRecordsAgg.set_index(['centerId']), on=['center_id'], how='left')
        centers_record = centers_record.where((pd.notnull(centers_record)), None)

        #print(centers_record['weeklyValue'].sum(), centers_record['confirmedBowler'].sum(), centers_record['projectedBowler'].sum())

        return centers_record, num

    @classmethod
    def get_center_info_detail(cls, center_id, start, end, type_, subType, dow, dowRange, dateRange, status, distinct,
                               pagination=False, page_size=None, offset=None, filters=None, sort=None, order=None):

        if sort and order:
            if order == 'desc':
                sort = '-' + sort
        else:
            sort = '-leagueId'

        leagueObjs = League.objects \
            .filter(centerId=center_id) \
            .exclude(confirmedBowlerCount__lt=8) \
            .order_by(sort)

        if dateRange == 'intersection':
            if start:
                leagueObjs = leagueObjs.exclude(end__lt=start)
            if end:
                leagueObjs = leagueObjs.exclude(start__gt=end)
        elif dateRange == 'specific':
            if start:
                leagueObjs = leagueObjs.filter(start__gte=start)
            if end:
                leagueObjs = leagueObjs.filter(end__lte=end)
        elif dateRange == 'ended':
            if start:
                leagueObjs = leagueObjs.exclude(end__lt=start)
            if end:
                leagueObjs = leagueObjs.exclude(start__gt=end).filter(end__lte=end)

        if type_:
            leagueObjs = leagueObjs.filter(reduce(operator.or_, (Q(leagueType__contains=i) for i in type_)))
        if subType:
            leagueObjs = leagueObjs.filter(reduce(operator.or_, (Q(leagueSubType__contains=i) for i in subType)))
        if status:
            leagueObjs = leagueObjs.filter(reduce(operator.or_, (Q(leagueStatus__contains=i) for i in status)))
        if dow:
            leagueObjs = leagueObjs.filter(reduce(operator.or_, (Q(dayOfWeekName__contains=dow_map[i]) for i in dow)))
        if distinct:
            leagueObjs = leagueObjs.filter(last=True)

        if filters:
            filters = ast.literal_eval(filters)

            for key, value in filters.items():
                filters_list = value.split(',')
                filters_list = [x.strip() for x in filters_list]
                filters[key] = filters_list
            if filters.get('leagueId'):
                filter_item = filters.get('leagueId')
                if len(filter_item) == 1:
                    leagueObjs = leagueObjs.filter(leagueId__icontains=filter_item[0])
                else:
                    leagueObjs = leagueObjs.filter(reduce(operator.or_,
                                                          (Q(leagueId__icontains=item)
                                                           for item in filter_item if item)))
            if filters.get('leagueName'):
                filter_item = filters.get('leagueName')
                if len(filter_item) == 1:
                    leagueObjs = leagueObjs.filter(leagueName__icontains=filter_item[0])
                else:
                    leagueObjs = leagueObjs.filter(reduce(operator.or_,
                                                          (Q(leagueName__icontains=item)
                                                           for item in filter_item if item)))
            if filters.get('start'):
                filter_item = filters.get('start')
                if len(filter_item) == 1:
                    leagueObjs = leagueObjs.filter(start__icontains=filter_item[0])
                else:
                    leagueObjs = leagueObjs.filter(reduce(operator.or_,
                                                          (Q(start__icontains=item)
                                                           for item in filter_item if item)))
            if filters.get('end'):
                filter_item = filters.get('end')
                if len(filter_item) == 1:
                    leagueObjs = leagueObjs.filter(end__icontains=filter_item[0])
                else:
                    leagueObjs = leagueObjs.filter(reduce(operator.or_,
                                                          (Q(end__icontains=item)
                                                           for item in filter_item if item)))
            if filters.get('startingLaneNumber'):
                filter_item = filters.get('startingLaneNumber')
                if len(filter_item) == 1:
                    leagueObjs = leagueObjs.filter(startingLaneNumber__icontains=filter_item[0])
                else:
                    leagueObjs = leagueObjs.filter(reduce(operator.or_,
                                                          (Q(startingLaneNumber__icontains=item)
                                                           for item in filter_item if item)))
            if filters.get('endingLaneNumber'):
                filter_item = filters.get('endingLaneNumber')
                if len(filter_item) == 1:
                    leagueObjs = leagueObjs.filter(endingLaneNumber__icontains=filter_item[0])
                else:
                    leagueObjs = leagueObjs.filter(reduce(operator.or_,
                                                          (Q(endingLaneNumber__icontains=item)
                                                           for item in filter_item if item)))
            if filters.get('bowlerEquivalentGoal'):
                filter_item = filters.get('bowlerEquivalentGoal')
                if len(filter_item) == 1:
                    leagueObjs = leagueObjs.filter(bowlerEquivalentGoal__icontains=filter_item[0])
                else:
                    leagueObjs = leagueObjs.filter(reduce(operator.or_,
                                                          (Q(bowlerEquivalentGoal__icontains=item)
                                                           for item in filter_item if item)))
            if filters.get('confirmedBowlerCount'):
                filter_item = filters.get('confirmedBowlerCount')
                if len(filter_item) == 1:
                    leagueObjs = leagueObjs.filter(confirmedBowlerCount__icontains=filter_item[0])
                else:
                    leagueObjs = leagueObjs.filter(reduce(operator.or_,
                                                          (Q(confirmedBowlerCount__icontains=item)
                                                           for item in filter_item if item)))
            if filters.get('bowlerEquivalentGoal'):
                filter_item = filters.get('bowlerEquivalentGoal')
                if len(filter_item) == 1:
                    leagueObjs = leagueObjs.filter(bowlerEquivalentGoal__icontains=filter_item[0])
                else:
                    leagueObjs = leagueObjs.filter(reduce(operator.or_,
                                                          (Q(bowlerEquivalentGoal__icontains=item)
                                                           for item in filter_item if item)))
            if filters.get('playersPerTeam'):
                filter_item = filters.get('playersPerTeam')
                if len(filter_item) == 1:
                    leagueObjs = leagueObjs.filter(playersPerTeam__icontains=filter_item[0])
                else:
                    leagueObjs = leagueObjs.filter(reduce(operator.or_,
                                                          (Q(playersPerTeam__icontains=item)
                                                           for item in filter_item if item)))
            if filters.get('numberOfTeams'):
                filter_item = filters.get('numberOfTeams')
                if len(filter_item) == 1:
                    leagueObjs = leagueObjs.filter(numberOfTeams__icontains=filter_item[0])
                else:
                    leagueObjs = leagueObjs.filter(reduce(operator.or_,
                                                          (Q(numberOfTeams__icontains=item)
                                                           for item in filter_item if item)))
            if filters.get('gamesPerPlayer'):
                filter_item = filters.get('gamesPerPlayer')
                if len(filter_item) == 1:
                    leagueObjs = leagueObjs.filter(gamesPerPlayer__icontains=filter_item[0])
                else:
                    leagueObjs = leagueObjs.filter(reduce(operator.or_,
                                                          (Q(gamesPerPlayer__icontains=item)
                                                           for item in filter_item if item)))
            if filters.get('lineageCost'):
                filter_item = filters.get('lineageCost')
                if len(filter_item) == 1:
                    leagueObjs = leagueObjs.filter(lineageCost__icontains=filter_item[0])
                else:
                    leagueObjs = leagueObjs.filter(reduce(operator.or_,
                                                          (Q(lineageCost__icontains=item)
                                                           for item in filter_item if item)))
            if filters.get('leagueFrequency'):
                filter_item = filters.get('leagueFrequency')
                if len(filter_item) == 1:
                    leagueObjs = leagueObjs.filter(leagueFrequency__icontains=filter_item[0])
                else:
                    leagueObjs = leagueObjs.filter(reduce(operator.or_,
                                                          (Q(leagueFrequency__icontains=item)
                                                           for item in filter_item if item)))
            if filters.get('currentYearLeagueNumber'):
                filter_item = filters.get('currentYearLeagueNumber')
                if len(filter_item) == 1:
                    leagueObjs = leagueObjs.filter(currentYearLeagueNumber__icontains=filter_item[0])
                else:
                    leagueObjs = leagueObjs.filter(reduce(operator.or_,
                                                          (Q(currentYearLeagueNumber__icontains=item)
                                                           for item in filter_item if item)))

        leagueRecords = pd.DataFrame.from_records(leagueObjs.values(
                                                                    'centerId',
                                                                    'leagueId',
                                                                    'leagueIdCopied',
                                                                    'leagueName',
                                                                    'leagueStatus',
                                                                    'start',
                                                                    'end',
                                                                    'dayOfWeekName',
                                                                    'daysPerWeek',
                                                                    'numberOfWeeks',
                                                                    'startingLaneNumber',
                                                                    'endingLaneNumber',
                                                                    'bowlerEquivalentGoal',
                                                                    'confirmedBowlerCount',
                                                                    'playersPerTeam',
                                                                    'numberOfTeams',
                                                                    'gamesPerPlayer',
                                                                    'lineageCost',
                                                                    'leagueFrequency',
                                                                    'currentYearLeagueNumber',
                                                                    ))

        if leagueRecords.empty:
            return pd.DataFrame(), 0

        # Formatting and Add columns
        dow_ = [dow_map[i] for i in dow]
        if dowRange == 'specific':
            leagueRecords['daysPerWeek'] = leagueRecords['dayOfWeekName'].apply(lambda x: len(set(x.split(',')) & set(dow_)))

        leagueRecords['start'] = leagueRecords['start'].dt.date
        leagueRecords['end'] = leagueRecords['end'].dt.date
        leagueRecords['endingLaneNumber'] = leagueRecords['endingLaneNumber'].astype(float)
        leagueRecords['startingLaneNumber'] = leagueRecords['startingLaneNumber'].astype(float)
        leagueRecords['lanes'] = leagueRecords['endingLaneNumber'] - leagueRecords['startingLaneNumber']
        leagueRecords['weeklyValue'] = (leagueRecords['daysPerWeek'] *
                                        leagueRecords['lineageCost'] *
                                        leagueRecords['bowlerEquivalentGoal'])
        leagueRecords['seasonalValue'] = (leagueRecords['weeklyValue'] * leagueRecords['numberOfWeeks'])
        leagueRecords['currentYearLeagueNumber'] = leagueRecords['currentYearLeagueNumber'].apply(lambda x: x.split('.')[0])

        #Calculate Revenue
        leagueRecords['leagueFrequency_'] = leagueRecords['leagueFrequency'].apply(lambda x: freqMap[x] if x else 2)
        leagueRecords['revPerDay'] = leagueRecords['lineageCost'] * leagueRecords['bowlerEquivalentGoal']
        leagueRecords['revDOW'] = leagueRecords['dayOfWeekName'] \
            .apply(lambda x: list(set(x.split(',')) & set(dow_)) if dow_ else x.split(','))

        # Calculate Revenue for Every weeks
        leagueRecords['start_'] = leagueRecords['start'].apply(lambda x: max(x, start))
        leagueRecords['end_'] = leagueRecords['end'].apply(lambda x: min(x, end))
        leagueRecords['revDOW_'] = leagueRecords['revDOW'].apply(lambda x: set([dow_map_reverse[i] for i in x]))
        leagueRecords['days'] = leagueRecords[['start_', 'end_', 'revDOW_']] \
            .apply(lambda x: days_in_range(x['start_'], x['end_'], x['revDOW_']), axis=1)
        leagueRecords = leagueRecords[leagueRecords['days'] != 0]
        leagueRecords['revenue'] = leagueRecords['days'] * leagueRecords['revPerDay']
        leagueRecords.drop('revDOW_', inplace=True, axis=1)

        for index, row in leagueRecords.iterrows():
            dates = pd.DataFrame(pd.date_range(row['start_'], row['end_']), columns=['date'])
            dates['value'] = 0
            dates['wom'] = dates['date'].apply(lambda x: week_of_month(x))
            dates['woy'] = dates['date'].apply(lambda x: x.isocalendar()[1])
            dates['dow'] = dates['date'].apply(lambda x: x.weekday() + 1)
            start_dow = dates.at[0, 'dow']

            if row['leagueFrequency_'] == 1:
                dates = dates[abs(dates['woy'] - start_dow) % 2 == 0]
                leagueRecords.at[index, 'weeklyValue'] = leagueRecords.at[index, 'weeklyValue'] / 2
            elif row['leagueFrequency_'] == 2:
                pass
            elif row['leagueFrequency_'] == 3:
                dates = dates[abs(dates['woy'] - start_dow) % 4 == 0]
                leagueRecords.at[index, 'weeklyValue'] = leagueRecords.at[index, 'weeklyValue'] / 4
            elif row['leagueFrequency_'] == 4:
                dates = dates[dates['wom'].isin([1])]
                leagueRecords.at[index, 'weeklyValue'] = leagueRecords.at[index, 'weeklyValue'] / 4
            elif row['leagueFrequency_'] == 5:
                dates = dates[dates['wom'].isin([3])]
                leagueRecords.at[index, 'weeklyValue'] = leagueRecords.at[index, 'weeklyValue'] / 4
            elif row['leagueFrequency_'] == 6:
                dates = dates[dates['wom'].isin([2])]
                leagueRecords.at[index, 'weeklyValue'] = leagueRecords.at[index, 'weeklyValue'] / 4
            elif row['leagueFrequency_'] == 7:
                dates = dates[dates['wom'].isin([2, 4])]
                leagueRecords.at[index, 'weeklyValue'] = leagueRecords.at[index, 'weeklyValue'] / 2
            elif row['leagueFrequency_'] == 8:
                dates = dates[dates['wom'].isin([4])]
                leagueRecords.at[index, 'weeklyValue'] = leagueRecords.at[index, 'weeklyValue'] / 4
            elif row['leagueFrequency_'] == 9:
                dates = dates[dates['wom'].isin([1, 3])]
                leagueRecords.at[index, 'weeklyValue'] = leagueRecords.at[index, 'weeklyValue'] / 2

            # Filter by revDOW
            revDOW = [dow_map_reverse[i] for i in row['revDOW']]
            dates = dates[dates['dow'].isin(revDOW)]

            leagueRecords.at[index, 'revenue'] = len(dates) * row['revPerDay']

        # Rounding
        leagueRecords['revenue'] = leagueRecords['revenue'].round(0)
        leagueRecords['weeklyValue'] = leagueRecords['weeklyValue'].round(0)
        leagueRecords['seasonalValue'] = leagueRecords['seasonalValue'].round(0)

        # Pagination
        leagueObjs = leagueObjs.filter(leagueId__in=leagueRecords['leagueId'].tolist())
        num = leagueObjs.count()

        if pagination:
            paginator = Paginator(leagueObjs, page_size, )
            current_page = int(offset / page_size) + 1
            leagueObjs = paginator.page(current_page).object_list

        return leagueRecords, num

    @classmethod
    def get_center_info_happen(cls, start, end, type_, subType, dow, dowRange, dateRange, status, distinct,
                        pagination=False, page_size=None, offset=None, filters=None, sort=None, order=None):

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
                    centers = centers.filter(reduce(operator.or_, (Q(center_name__icontains=item) for item in filter_item if item)))
            if filters.get('region'):
                filter_item = filters.get('region')
                if len(filter_item) == 1:
                    centers = centers.filter(region__icontains=filter_item[0])
                else:
                    centers = centers.filter(reduce(operator.or_, (Q(region__icontains=item) for item in filter_item if item)))
            if filters.get('district'):
                filter_item = filters.get('district')
                if len(filter_item) == 1:
                    centers = centers.filter(district__icontains=filter_item[0])
                else:
                    centers = centers.filter(reduce(operator.or_, (Q(district__icontains=item) for item in filter_item if item)))

        num = centers.count()

        if pagination:
            paginator = Paginator(centers, page_size,)
            current_page = int(offset/page_size) + 1
            centers = paginator.page(current_page).object_list

        centers_id_list = centers.values_list('center_id', flat=True)

        centers_record = pd.DataFrame.from_records(centers.values(
                                                           'center_id',
                                                           'center_name',
                                                           'region',
                                                           'district',
                                                           ))

        if centers_record.empty:
            return pd.DataFrame(), 0

        # Start to calculate league statistics
        # Filter data
        leagueObjs = League.objects.filter(centerId__in=centers_id_list).exclude(confirmedBowlerCount__lt=8)
        if dateRange == 'intersection':
            if start:
                leagueObjs = leagueObjs.exclude(end__lt=start)
            if end:
                leagueObjs = leagueObjs.exclude(start__gt=end)
        elif dateRange == 'specific':
            if start:
                leagueObjs = leagueObjs.filter(start__gte=start)
            if end:
                leagueObjs = leagueObjs.filter(end__lte=end)
        elif dateRange == 'ended':
            if start:
                leagueObjs = leagueObjs.exclude(end__lt=start)
            if end:
                leagueObjs = leagueObjs.exclude(start__gt=end).filter(end__lte=end)

        if type_:
            leagueObjs = leagueObjs.filter(reduce(operator.or_, (Q(leagueType__contains=i) for i in type_)))
        if subType:
            leagueObjs = leagueObjs.filter(reduce(operator.or_, (Q(leagueSubType__contains=i) for i in subType)))
        if status:
            leagueObjs = leagueObjs.filter(reduce(operator.or_, (Q(leagueStatus__contains=i) for i in status)))
        if dow:
            leagueObjs = leagueObjs.filter(reduce(operator.or_, (Q(dayOfWeekName__contains=dow_map[i]) for i in dow)))
        if distinct:
            leagueObjs = leagueObjs.filter(last=True)

        leagueRecords = pd.DataFrame.from_records(leagueObjs.values('centerId',
                                                                    'leagueId',
                                                                    'start',
                                                                    'end',
                                                                    'dayOfWeekName',
                                                                    'daysPerWeek',
                                                                    'numberOfWeeks',
                                                                    'startingLaneNumber',
                                                                    'endingLaneNumber',
                                                                    'bowlerEquivalentGoal',
                                                                    'confirmedBowlerCount',
                                                                    'playersPerTeam',
                                                                    'numberOfTeams',
                                                                    'gamesPerPlayer',
                                                                    'lineageCost',
                                                                    'leagueFrequency',
                                                                    ))

        if leagueRecords.empty:
            return centers_record, num

        dow_ = [dow_map[i] for i in dow]
        # Add columns
        leagueRecords['start'] = leagueRecords['start'].dt.date
        leagueRecords['end'] = leagueRecords['end'].dt.date
        if dowRange == 'specific':
            leagueRecords['daysPerWeek'] = leagueRecords['dayOfWeekName'].apply(lambda x: len(set(x.split(',')) & set(dow_)))
        leagueRecords['sumGames'] = leagueRecords['bowlerEquivalentGoal'] * leagueRecords['gamesPerPlayer']
        leagueRecords['weeklyValue'] = leagueRecords['daysPerWeek'] * leagueRecords['lineageCost'] * leagueRecords['bowlerEquivalentGoal']
        leagueRecords['seasonalValue'] = leagueRecords['weeklyValue'] * leagueRecords['numberOfWeeks']

        # Calculate Revenue
        leagueRecords['leagueFrequency_'] = leagueRecords['leagueFrequency'].apply(lambda x: freqMap[x] if x else 2)
        leagueRecords['revPerDay'] = leagueRecords['lineageCost'] * leagueRecords['bowlerEquivalentGoal']
        leagueRecords['revDOW'] = leagueRecords['dayOfWeekName'] \
            .apply(lambda x: list(set(x.split(',')) & set(dow_)) if dow_ else x.split(','))

        # minWeeks Min week = min(NumberOfWeeks) = min(36,12,10)=10
        # maxWeeks Max week = max(NumberOfWeeks) = max(36,12,10)=36
        # avgPlayersPerTeam Avg Players/Team = sum(confirmed)/sum(team) = (40+30+16)/(10+8+6)=3.58
        # avgPlayersPerLeague Avg Players/League = sum(confirmed)/count(league) = (40+30+16)/3=28.7
        # avgTeamsPerLeague Avg Teams/League = sum(team)/count(league) = (10+8+6)/3=8
        # avgGamesPerBowler Avg Games/Bowler = sum(confirmed * GamesPerPlayer)/sum(confirmed) = (40*5+30*4+16*3)/(40+30+16)=4.28
        # avgGamesPerLeague Avg Games/League = sum(confirmed * GamesPerPlayer)/count(league) = (40*5+30*4+16*3)/3=122.7
        # avgLineagePerLeague Avg Lineage$/League = sum(LineageCost)/count(league) = (10+12+13)/3=11.7
        # avgLineagePerGame Avg Lineage$/Game = sum(LineageCost)/sum(GamesPerPlayer) = (10+12+13)/(5+4+3)=2.9
        # avgLineagePerBowler Avg Lineage$/Bowler = sum(LineageCost*confirmed)/sum(confirmed) = (10*40+12*30+13*16)/(40+30+16)=11.3
        # weeklyValue Weekly Value (By Center) = sum(DaysPerWeek * LineageCost * confirmed) = 3*10*40+1*12*30+2*13*16 = $1976
        # avgWeeklyValue seasonalValue Avg Weekly Value = sum(DaysPerWeek * LineageCost * confirmed)/count(league) = (3*10*40+1*12*30+2*13*16)/3 = $658.7
        # seasonalValue Seasonal Value (By Center) = sum(NumberOfWeeks * DaysPerWeek * LineageCost * confirmed) = 36*3*10*40+12*1*12*30+10*2*13*16 = $51680
        # avgSeasonalValue Avg Seasonal Value = sum(NumberOfWeeks * DaysPerWeek * LineageCost * confirmed)/count(league) = (36*3*10*40+12*1*12*30+10*2*13*16)/3 = $17226.7

        # Aggregate Data
        def agg(x):
            revenue = 0
            revenue += x[x['leagueFrequency_'] == 2]['revenue'].sum()

            for index, row in x[x['leagueFrequency_'] != 2].iterrows():
                dates = pd.DataFrame(pd.date_range(row['start_'], row['end_']), columns=['date'])
                dates['value'] = 0
                dates['wom'] = dates['date'].apply(lambda x: week_of_month(x))
                dates['woy'] = dates['date'].apply(lambda x: x.isocalendar()[1])
                dates['dow'] = dates['date'].apply(lambda x: x.weekday() + 1)
                start_dow = dates.at[0, 'dow']

                if row['leagueFrequency_'] == 1:
                    dates = dates[abs(dates['woy'] - start_dow) % 2 == 0]
                    x.at[index, 'weeklyValue'] = x.at[index, 'weeklyValue'] / 2
                elif row['leagueFrequency_'] == 2:
                    pass
                elif row['leagueFrequency_'] == 3:
                    dates = dates[abs(dates['woy'] - start_dow) % 4 == 0]
                    x.at[index, 'weeklyValue'] = x.at[index, 'weeklyValue'] / 4
                elif row['leagueFrequency_'] == 4:
                    dates = dates[dates['wom'].isin([1])]
                    x.at[index, 'weeklyValue'] = x.at[index, 'weeklyValue'] / 4
                elif row['leagueFrequency_'] == 5:
                    dates = dates[dates['wom'].isin([3])]
                    x.at[index, 'weeklyValue'] = x.at[index, 'weeklyValue'] / 4
                elif row['leagueFrequency_'] == 6:
                    dates = dates[dates['wom'].isin([2])]
                    x.at[index, 'weeklyValue'] = x.at[index, 'weeklyValue'] / 4
                elif row['leagueFrequency_'] == 7:
                    dates = dates[dates['wom'].isin([2, 4])]
                    x.at[index, 'weeklyValue'] = x.at[index, 'weeklyValue'] / 2
                elif row['leagueFrequency_'] == 8:
                    dates = dates[dates['wom'].isin([4])]
                    x.at[index, 'weeklyValue'] = x.at[index, 'weeklyValue'] / 4
                elif row['leagueFrequency_'] == 9:
                    dates = dates[dates['wom'].isin([1, 3])]
                    x.at[index, 'weeklyValue'] = x.at[index, 'weeklyValue'] / 2

                # Filter by revDOW
                revDOW = [dow_map_reverse[i] for i in row['revDOW']]
                dates = dates[dates['dow'].isin(revDOW)]

                revenue += len(dates) * row['revPerDay']

            count = len(x)
            sumConfirmedBowlerCount = x['bowlerEquivalentGoal'].sum()
            sumNumberOfTeams = x['numberOfTeams'].sum()
            sumGames = (x['sumGames']).sum()
            sumLineageCost = x['lineageCost'].sum()
            SumWeeklyValue = x['weeklyValue'].sum()
            SumSeasonalValue = x['seasonalValue'].sum()

            res = pd.Series(
                {
                    'minWeeks': min(x['numberOfWeeks']),
                    'maxWeeks': max(x['numberOfWeeks']),
                    'avgPlayersPerTeam': round(sumConfirmedBowlerCount / sumNumberOfTeams, 2),
                    'avgPlayersPerLeague': round(sumConfirmedBowlerCount / count, 2),
                    'avgTeamsPerLeague': round(sumNumberOfTeams / count, 2),
                    'avgGamesPerBowler': round(sumGames / sumConfirmedBowlerCount, 2),
                    'avgGamesPerLeague': round(sumGames / count, 2),
                    'avgLineagePerLeague': round(sumLineageCost / count, 2),
                    'avgLineagePerGame': round(sumLineageCost / x['gamesPerPlayer'].sum(), 2),
                    'avgLineagePerBowler': round(sumLineageCost / sumConfirmedBowlerCount, 2),
                    'confirmedBowler': round(sumConfirmedBowlerCount, 0),
                    'weeklyValue': round(SumWeeklyValue, 0),
                    'avgWeeklyValue': round(SumWeeklyValue / count, 0),
                    'seasonalValue': round(SumSeasonalValue, 0),
                    'avgSeasonalValue': round(SumSeasonalValue / count, 0),
                    'revenue': round(revenue, 0) if revenue > 0 else None,
                }
            )

            return res

        leagueRecords['start_'] = leagueRecords['start'].apply(lambda x: max(x, start))
        leagueRecords['end_'] = leagueRecords['end'].apply(lambda x: min(x, end))
        leagueRecords['revDOW_'] = leagueRecords['revDOW'].apply(lambda x: set([dow_map_reverse[i] for i in x]))
        leagueRecords['days'] = leagueRecords[['start_', 'end_', 'revDOW_']] \
            .apply(lambda x: days_in_range(x['start_'], x['end_'], x['revDOW_']), axis=1)
        leagueRecords['revenue'] = leagueRecords['days'] * leagueRecords['revPerDay']

        leagueRecordsAgg = pd.DataFrame(leagueRecords.groupby(['centerId'])
                                                     .apply(agg),
                                        columns=[
                                            'minWeeks',
                                            'maxWeeks',
                                            'avgPlayersPerTeam',
                                            'avgPlayersPerLeague',
                                            'avgTeamsPerLeague',
                                            'avgGamesPerBowler',
                                            'avgGamesPerLeague',
                                            'avgLineagePerLeague',
                                            'avgLineagePerGame',
                                            'avgLineagePerBowler',
                                            'confirmedBowler',
                                            # 'projectedBowler',
                                            'weeklyValue',
                                            'avgWeeklyValue',
                                            'projectedWeeklyValue',
                                            'seasonalValue',
                                            'avgSeasonalValue',
                                            'revenue'
                                            ]
                                        )

        leagueRecordsAgg.reset_index(inplace=True)

        # Left join league stats to center table
        leagueRecordsAgg['centerId'] = leagueRecordsAgg['centerId'].apply(int)
        centers_record = centers_record.join(leagueRecordsAgg.set_index(['centerId']), on=['center_id'], how='left')
        centers_record = centers_record.where((pd.notnull(centers_record)), None)

        #print(centers_record['weeklyValue'].sum(), centers_record['confirmedBowler'].sum(), centers_record['projectedBowler'].sum())

        # Monetarize
        moneyFields = ['avgLineagePerLeague', 'avgLineagePerGame', 'avgLineagePerBowler',
                       'weeklyValue', 'avgWeeklyValue',
                       'seasonalValue', 'avgSeasonalValue', 'revenue']
        for field in moneyFields:
            centers_record[field] = centers_record[field].apply(lambda x: str(int(x)) if x else x)
            centers_record[field] = centers_record[field].apply(lambda x: '${price}'.format(price=x) if x else None)

        return centers_record, num

    @classmethod
    def get_center_info_detail_happen(cls, center_id, start, end, type_, subType, dow, dowRange, dateRange, status, distinct,
                               pagination=False, page_size=None, offset=None, filters=None, sort=None, order=None):

        if sort and order:
            if order == 'desc':
                sort = '-' + sort
        else:
            sort = '-leagueId'

        leagueObjs = League.objects \
            .filter(centerId=center_id) \
            .exclude(confirmedBowlerCount__lt=8) \
            .order_by(sort)

        if dateRange == 'intersection':
            if start:
                leagueObjs = leagueObjs.exclude(end__lt=start)
            if end:
                leagueObjs = leagueObjs.exclude(start__gt=end)
        elif dateRange == 'specific':
            if start:
                leagueObjs = leagueObjs.filter(start__gte=start)
            if end:
                leagueObjs = leagueObjs.filter(end__lte=end)
        elif dateRange == 'ended':
            if start:
                leagueObjs = leagueObjs.exclude(end__lt=start)
            if end:
                leagueObjs = leagueObjs.exclude(start__gt=end).filter(end__lte=end)

        if type_:
            leagueObjs = leagueObjs.filter(reduce(operator.or_, (Q(leagueType__contains=i) for i in type_)))
        if subType:
            leagueObjs = leagueObjs.filter(reduce(operator.or_, (Q(leagueSubType__contains=i) for i in subType)))
        if status:
            leagueObjs = leagueObjs.filter(reduce(operator.or_, (Q(leagueStatus__contains=i) for i in status)))
        if dow:
            leagueObjs = leagueObjs.filter(reduce(operator.or_, (Q(dayOfWeekName__contains=dow_map[i]) for i in dow)))
        if distinct:
            leagueObjs = leagueObjs.filter(last=True)

        if filters:
            filters = ast.literal_eval(filters)

            for key, value in filters.items():
                filters_list = value.split(',')
                filters_list = [x.strip() for x in filters_list]
                filters[key] = filters_list
            if filters.get('leagueId'):
                filter_item = filters.get('leagueId')
                if len(filter_item) == 1:
                    leagueObjs = leagueObjs.filter(leagueId__icontains=filter_item[0])
                else:
                    leagueObjs = leagueObjs.filter(reduce(operator.or_,
                                                          (Q(leagueId__icontains=item)
                                                           for item in filter_item if item)))
            if filters.get('leagueName'):
                filter_item = filters.get('leagueName')
                if len(filter_item) == 1:
                    leagueObjs = leagueObjs.filter(leagueName__icontains=filter_item[0])
                else:
                    leagueObjs = leagueObjs.filter(reduce(operator.or_,
                                                          (Q(leagueName__icontains=item)
                                                           for item in filter_item if item)))
            if filters.get('start'):
                filter_item = filters.get('start')
                if len(filter_item) == 1:
                    leagueObjs = leagueObjs.filter(start__icontains=filter_item[0])
                else:
                    leagueObjs = leagueObjs.filter(reduce(operator.or_,
                                                          (Q(start__icontains=item)
                                                           for item in filter_item if item)))
            if filters.get('end'):
                filter_item = filters.get('end')
                if len(filter_item) == 1:
                    leagueObjs = leagueObjs.filter(end__icontains=filter_item[0])
                else:
                    leagueObjs = leagueObjs.filter(reduce(operator.or_,
                                                          (Q(end__icontains=item)
                                                           for item in filter_item if item)))
            if filters.get('startingLaneNumber'):
                filter_item = filters.get('startingLaneNumber')
                if len(filter_item) == 1:
                    leagueObjs = leagueObjs.filter(startingLaneNumber__icontains=filter_item[0])
                else:
                    leagueObjs = leagueObjs.filter(reduce(operator.or_,
                                                          (Q(startingLaneNumber__icontains=item)
                                                           for item in filter_item if item)))
            if filters.get('endingLaneNumber'):
                filter_item = filters.get('endingLaneNumber')
                if len(filter_item) == 1:
                    leagueObjs = leagueObjs.filter(endingLaneNumber__icontains=filter_item[0])
                else:
                    leagueObjs = leagueObjs.filter(reduce(operator.or_,
                                                          (Q(endingLaneNumber__icontains=item)
                                                           for item in filter_item if item)))
            if filters.get('bowlerEquivalentGoal'):
                filter_item = filters.get('bowlerEquivalentGoal')
                if len(filter_item) == 1:
                    leagueObjs = leagueObjs.filter(bowlerEquivalentGoal__icontains=filter_item[0])
                else:
                    leagueObjs = leagueObjs.filter(reduce(operator.or_,
                                                          (Q(bowlerEquivalentGoal__icontains=item)
                                                           for item in filter_item if item)))
            if filters.get('confirmedBowlerCount'):
                filter_item = filters.get('confirmedBowlerCount')
                if len(filter_item) == 1:
                    leagueObjs = leagueObjs.filter(confirmedBowlerCount__icontains=filter_item[0])
                else:
                    leagueObjs = leagueObjs.filter(reduce(operator.or_,
                                                          (Q(confirmedBowlerCount__icontains=item)
                                                           for item in filter_item if item)))
            if filters.get('bowlerEquivalentGoal'):
                filter_item = filters.get('bowlerEquivalentGoal')
                if len(filter_item) == 1:
                    leagueObjs = leagueObjs.filter(bowlerEquivalentGoal__icontains=filter_item[0])
                else:
                    leagueObjs = leagueObjs.filter(reduce(operator.or_,
                                                          (Q(bowlerEquivalentGoal__icontains=item)
                                                           for item in filter_item if item)))
            if filters.get('playersPerTeam'):
                filter_item = filters.get('playersPerTeam')
                if len(filter_item) == 1:
                    leagueObjs = leagueObjs.filter(playersPerTeam__icontains=filter_item[0])
                else:
                    leagueObjs = leagueObjs.filter(reduce(operator.or_,
                                                          (Q(playersPerTeam__icontains=item)
                                                           for item in filter_item if item)))
            if filters.get('numberOfTeams'):
                filter_item = filters.get('numberOfTeams')
                if len(filter_item) == 1:
                    leagueObjs = leagueObjs.filter(numberOfTeams__icontains=filter_item[0])
                else:
                    leagueObjs = leagueObjs.filter(reduce(operator.or_,
                                                          (Q(numberOfTeams__icontains=item)
                                                           for item in filter_item if item)))
            if filters.get('gamesPerPlayer'):
                filter_item = filters.get('gamesPerPlayer')
                if len(filter_item) == 1:
                    leagueObjs = leagueObjs.filter(gamesPerPlayer__icontains=filter_item[0])
                else:
                    leagueObjs = leagueObjs.filter(reduce(operator.or_,
                                                          (Q(gamesPerPlayer__icontains=item)
                                                           for item in filter_item if item)))
            if filters.get('lineageCost'):
                filter_item = filters.get('lineageCost')
                if len(filter_item) == 1:
                    leagueObjs = leagueObjs.filter(lineageCost__icontains=filter_item[0])
                else:
                    leagueObjs = leagueObjs.filter(reduce(operator.or_,
                                                          (Q(lineageCost__icontains=item)
                                                           for item in filter_item if item)))
            if filters.get('leagueFrequency'):
                filter_item = filters.get('leagueFrequency')
                if len(filter_item) == 1:
                    leagueObjs = leagueObjs.filter(leagueFrequency__icontains=filter_item[0])
                else:
                    leagueObjs = leagueObjs.filter(reduce(operator.or_,
                                                          (Q(leagueFrequency__icontains=item)
                                                           for item in filter_item if item)))
            if filters.get('currentYearLeagueNumber'):
                filter_item = filters.get('currentYearLeagueNumber')
                if len(filter_item) == 1:
                    leagueObjs = leagueObjs.filter(currentYearLeagueNumber__icontains=filter_item[0])
                else:
                    leagueObjs = leagueObjs.filter(reduce(operator.or_,
                                                          (Q(currentYearLeagueNumber__icontains=item)
                                                           for item in filter_item if item)))

        num = leagueObjs.count()

        if pagination:
            paginator = Paginator(leagueObjs, page_size, )
            current_page = int(offset / page_size) + 1
            leagueObjs = paginator.page(current_page).object_list

        leagueRecords = pd.DataFrame.from_records(leagueObjs.values(
                                                                    'leagueId',
                                                                    'leagueIdCopied',
                                                                    'leagueName',
                                                                    'leagueStatus',
                                                                    'start',
                                                                    'end',
                                                                    'dayOfWeekName',
                                                                    'daysPerWeek',
                                                                    'numberOfWeeks',
                                                                    'startingLaneNumber',
                                                                    'endingLaneNumber',
                                                                    'bowlerEquivalentGoal',
                                                                    'confirmedBowlerCount',
                                                                    'playersPerTeam',
                                                                    'numberOfTeams',
                                                                    'gamesPerPlayer',
                                                                    'lineageCost',
                                                                    'leagueFrequency',
                                                                    'currentYearLeagueNumber',
                                                                    ))

        if leagueRecords.empty:
            return pd.DataFrame(), 0

        # Formatting and Add columns
        dow_ = [dow_map[i] for i in dow]
        if dowRange == 'specific':
            leagueRecords['daysPerWeek'] = leagueRecords['dayOfWeekName'].apply(lambda x: len(set(x.split(',')) & set(dow_)))

        leagueRecords['start'] = leagueRecords['start'].dt.date
        leagueRecords['end'] = leagueRecords['end'].dt.date
        leagueRecords['endingLaneNumber'] = leagueRecords['endingLaneNumber'].astype(float)
        leagueRecords['startingLaneNumber'] = leagueRecords['startingLaneNumber'].astype(float)
        leagueRecords['lanes'] = leagueRecords['endingLaneNumber'] - leagueRecords['startingLaneNumber']
        leagueRecords['weeklyValue'] = (leagueRecords['daysPerWeek'] *
                                        leagueRecords['lineageCost'] *
                                        leagueRecords['bowlerEquivalentGoal']).round(0)
        leagueRecords['seasonalValue'] = (leagueRecords['weeklyValue'] * leagueRecords['numberOfWeeks']).round(0)
        leagueRecords['currentYearLeagueNumber'] = leagueRecords['currentYearLeagueNumber'].apply(lambda x: x.split('.')[0])

        #Calculate Revenue
        leagueRecords['leagueFrequency_'] = leagueRecords['leagueFrequency'].apply(lambda x: freqMap[x] if x else 2)
        leagueRecords['revPerDay'] = leagueRecords['lineageCost'] * leagueRecords['bowlerEquivalentGoal']
        leagueRecords['revDOW'] = leagueRecords['dayOfWeekName'] \
            .apply(lambda x: list(set(x.split(',')) & set(dow_)) if dow_ else x.split(','))

        # Calculate Revenue for Every weeks
        leagueRecords['start_'] = leagueRecords['start'].apply(lambda x: max(x, start))
        leagueRecords['end_'] = leagueRecords['end'].apply(lambda x: min(x, end))
        leagueRecords['revDOW_'] = leagueRecords['revDOW'].apply(lambda x: set([dow_map_reverse[i] for i in x]))
        leagueRecords['days'] = leagueRecords[['start_', 'end_', 'revDOW_']] \
            .apply(lambda x: days_in_range(x['start_'], x['end_'], x['revDOW_']), axis=1)
        leagueRecords['revenue'] = leagueRecords['days'] * leagueRecords['revPerDay']
        leagueRecords.drop('revDOW_', inplace=True, axis=1)

        for index, row in leagueRecords.iterrows():
            dates = pd.DataFrame(pd.date_range(row['start_'], row['end_']), columns=['date'])
            dates['value'] = 0
            dates['wom'] = dates['date'].apply(lambda x: week_of_month(x))
            dates['woy'] = dates['date'].apply(lambda x: x.isocalendar()[1])
            dates['dow'] = dates['date'].apply(lambda x: x.weekday() + 1)
            start_dow = dates.at[0, 'dow']

            if row['leagueFrequency_'] == 1:
                dates = dates[abs(dates['woy'] - start_dow) % 2 == 0]
                leagueRecords.at[index, 'weeklyValue'] = leagueRecords.at[index, 'weeklyValue'] / 2
            elif row['leagueFrequency_'] == 2:
                pass
            elif row['leagueFrequency_'] == 3:
                dates = dates[abs(dates['woy'] - start_dow) % 4 == 0]
                leagueRecords.at[index, 'weeklyValue'] = leagueRecords.at[index, 'weeklyValue'] / 4
            elif row['leagueFrequency_'] == 4:
                dates = dates[dates['wom'].isin([1])]
                leagueRecords.at[index, 'weeklyValue'] = leagueRecords.at[index, 'weeklyValue'] / 4
            elif row['leagueFrequency_'] == 5:
                dates = dates[dates['wom'].isin([3])]
                leagueRecords.at[index, 'weeklyValue'] = leagueRecords.at[index, 'weeklyValue'] / 4
            elif row['leagueFrequency_'] == 6:
                dates = dates[dates['wom'].isin([2])]
                leagueRecords.at[index, 'weeklyValue'] = leagueRecords.at[index, 'weeklyValue'] / 4
            elif row['leagueFrequency_'] == 7:
                dates = dates[dates['wom'].isin([2, 4])]
                leagueRecords.at[index, 'weeklyValue'] = leagueRecords.at[index, 'weeklyValue'] / 2
            elif row['leagueFrequency_'] == 8:
                dates = dates[dates['wom'].isin([4])]
                leagueRecords.at[index, 'weeklyValue'] = leagueRecords.at[index, 'weeklyValue'] / 4
            elif row['leagueFrequency_'] == 9:
                dates = dates[dates['wom'].isin([1, 3])]
                leagueRecords.at[index, 'weeklyValue'] = leagueRecords.at[index, 'weeklyValue'] / 2

            # Filter by revDOW
            revDOW = [dow_map_reverse[i] for i in row['revDOW']]
            dates = dates[dates['dow'].isin(revDOW)]

            leagueRecords.at[index, 'revenue'] = round(len(dates) * row['revPerDay'], 0)

        # Monetarize
        moneyFields = ['lineageCost', 'weeklyValue', 'seasonalValue', 'revenue']
        for field in moneyFields:
            leagueRecords[field] = leagueRecords[field].apply(lambda x: str(int(x)) if x and x % 1 == 0 else x)
            leagueRecords[field] = leagueRecords[field].apply(lambda x: '${price}'.format(price=x) if x else None)

        return leagueRecords, num

    @classmethod
    def get_center_info_transact(cls, start, end, type_, subType, dow, dowRange, dateRange, status, distinct,
                        pagination=False, page_size=None, offset=None, filters=None, sort=None, order=None):

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
                    centers = centers.filter(reduce(operator.or_, (Q(center_name__icontains=item) for item in filter_item if item)))
            if filters.get('region'):
                filter_item = filters.get('region')
                if len(filter_item) == 1:
                    centers = centers.filter(region__icontains=filter_item[0])
                else:
                    centers = centers.filter(reduce(operator.or_, (Q(region__icontains=item) for item in filter_item if item)))
            if filters.get('district'):
                filter_item = filters.get('district')
                if len(filter_item) == 1:
                    centers = centers.filter(district__icontains=filter_item[0])
                else:
                    centers = centers.filter(reduce(operator.or_, (Q(district__icontains=item) for item in filter_item if item)))

        num = centers.count()

        if pagination:
            paginator = Paginator(centers, page_size,)
            current_page = int(offset/page_size) + 1
            centers = paginator.page(current_page).object_list

        centers_id_list = centers.values_list('center_id', flat=True)

        centers_record = pd.DataFrame.from_records(centers.values(
                                                           'center_id',
                                                           'center_name',
                                                           'region',
                                                           'district',
                                                           ))

        if centers_record.empty:

            return pd.DataFrame(), 0

        # Start to calculate league statistics
        # .using('dev') \
        leagueObjs = LeagueTransaction.objects \
            .filter(
                centerId__in=centers_id_list,
                businessDate__gte=start,
                businessDate__lte=end
            )

        if dateRange == 'intersection':
            if start:
                leagueObjs = leagueObjs.exclude(end__lt=start)
            if end:
                leagueObjs = leagueObjs.exclude(start__gt=end)
        elif dateRange == 'specific':
            if start:
                leagueObjs = leagueObjs.filter(start__gte=start)
            if end:
                leagueObjs = leagueObjs.filter(end__lte=end)
        elif dateRange == 'ended':
            if start:
                leagueObjs = leagueObjs.exclude(end__lt=start)
            if end:
                leagueObjs = leagueObjs.exclude(start__gt=end).filter(end__lte=end)

        if type_:
            leagueObjs = leagueObjs.filter(reduce(operator.or_, (Q(leagueType__contains=i) for i in type_)))
        if subType:
            leagueObjs = leagueObjs.filter(reduce(operator.or_, (Q(leagueSubType__contains=i) for i in subType)))
        if status:
            leagueObjs = leagueObjs.filter(reduce(operator.or_, (Q(leagueStatus__contains=i) for i in status)))
        if dow:
            leagueObjs = leagueObjs.filter(reduce(operator.or_, (Q(dayOfWeekName__contains=dow_map[i]) for i in dow)))

        leagueRecords = pd.DataFrame.from_records(leagueObjs.values('centerId',
                                                                    'leagueId',
                                                                    'revenueAmount',
                                                                    'daysPerWeek',
                                                                    'numberOfWeeks',
                                                                    ))

        if leagueRecords.empty:
            return pd.DataFrame(), num

        # Calculate Weekly and Seasonal
        leagueRecords_ = pd.pivot_table(leagueRecords,
                                        index=['centerId', 'leagueId', 'daysPerWeek', 'numberOfWeeks', ],
                                        columns=[],
                                        values=['revenueAmount'],
                                        aggfunc=lambda x: sum(x) / len(x)
                                        )
        leagueRecords_.reset_index(inplace=True)
        leagueRecords_['revenue_transact_weekly'] = leagueRecords_['revenueAmount'] * leagueRecords_['daysPerWeek']
        leagueRecords_['revenue_transact_seasonal'] = leagueRecords_['revenueAmount'] * leagueRecords_['daysPerWeek'] * leagueRecords_['numberOfWeeks']
        leagueRecords_ = pd.pivot_table(leagueRecords_,
                                        index=['centerId'],
                                        columns=[],
                                        values=['revenue_transact_weekly', 'revenue_transact_seasonal'],
                                        aggfunc='sum'
                                        )
        leagueRecords_.reset_index(inplace=True)
        # Calculate Rev
        leagueRecords = pd.pivot_table(leagueRecords,
                                       index=['centerId'],
                                       columns=[],
                                       values=['revenueAmount'],
                                       aggfunc='sum'
                                       )
        leagueRecords.reset_index(inplace=True)
        leagueRecords = leagueRecords.join(leagueRecords_.set_index(['centerId']), on=['centerId'], how='left')
        leagueRecords.rename({'revenueAmount': 'revenue_transact',
                              'centerId': 'center_id'
                              }, axis=1, inplace=True)

        leagueRecords['center_id'] = leagueRecords['center_id'].astype(int)
        leagueRecords = leagueRecords.where((pd.notnull(leagueRecords)), None)

        return leagueRecords, num

    @classmethod
    def get_center_info_transact_detail(cls, center_id, start, end, type_, subType, dow, dowRange, dateRange, status, distinct,
                                 pagination=False, page_size=None, offset=None, filters=None, sort=None, order=None):

        if sort and order:
            if order == 'desc':
                sort = '-' + sort
        else:
            sort = '-leagueId'

        # Start to calculate league statistics
        # .using('dev')
        leagueObjs = LeagueTransaction.objects \
            .filter(
            centerId=center_id,
            businessDate__gte=start,
            businessDate__lte=end
        )

        if type_:
            leagueObjs = leagueObjs.filter(reduce(operator.or_, (Q(leagueType__contains=i) for i in type_)))
        if subType:
            leagueObjs = leagueObjs.filter(reduce(operator.or_, (Q(leagueSubType__contains=i) for i in subType)))
        if status:
            leagueObjs = leagueObjs.filter(reduce(operator.or_, (Q(leagueStatus__contains=i) for i in status)))
        if dow:
            leagueObjs = leagueObjs.filter(reduce(operator.or_, (Q(dayOfWeekName__contains=dow_map[i]) for i in dow)))

        # Filter by different dateRange type
        if dateRange == 'intersection':
            if start:
                leagueObjs = leagueObjs.exclude(end__lt=start)
            if end:
                leagueObjs = leagueObjs.exclude(start__gt=end)
        elif dateRange == 'specific':
            if start:
                leagueObjs = leagueObjs.filter(start__gte=start)
            if end:
                leagueObjs = leagueObjs.filter(end__lte=end)
        elif dateRange == 'ended':
            if start:
                leagueObjs = leagueObjs.exclude(end__lt=start)
            if end:
                leagueObjs = leagueObjs.exclude(start__gt=end).filter(end__lte=end)

        leagueRecords = pd.DataFrame.from_records(leagueObjs.values(
                                                                    'leagueId',
                                                                    'revenueAmount',
                                                                    'daysPerWeek',
                                                                    'numberOfWeeks',
                                                                    ))

        if leagueRecords.empty:
            return pd.DataFrame(), 0

        leagueRecords_ = pd.pivot_table(leagueRecords,
                                        index=['leagueId', 'daysPerWeek', 'numberOfWeeks', ],
                                        columns=[],
                                        values=['revenueAmount'],
                                        aggfunc=lambda x: sum(x) / len(x)
                                        )

        leagueRecords_.reset_index(inplace=True)
        leagueRecords_['revenue_transact_weekly'] = leagueRecords_['revenueAmount'] * leagueRecords_['daysPerWeek']
        leagueRecords_['revenue_transact_seasonal'] = leagueRecords_['revenueAmount'] * leagueRecords_['daysPerWeek'] * \
                                                     leagueRecords_['numberOfWeeks']
        leagueRecords_.drop('revenueAmount', axis=1, inplace=True)

        # Calculate Rev
        leagueRecords = pd.pivot_table(leagueRecords,
                                       index=['leagueId'],
                                       columns=[],
                                       values=['revenueAmount'],
                                       aggfunc='sum'
                                       )
        leagueRecords.reset_index(inplace=True)
        leagueRecords = leagueRecords.join(leagueRecords_.set_index(['leagueId']), on=['leagueId'], how='left')

        leagueRecords.rename({'revenueAmount': 'revenue_transact'}, axis=1, inplace=True)
        leagueRecords = leagueRecords[['leagueId',
                                       'revenue_transact',
                                       'revenue_transact_weekly',
                                       'revenue_transact_seasonal']]

        return leagueRecords, len(leagueRecords)

    @classmethod
    def get_center_info_food(cls, start, end, type_, subType, dow, dowRange, dateRange, status, distinct,
                        pagination=False, page_size=None, offset=None, filters=None, sort=None, order=None):

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
                    centers = centers.filter(reduce(operator.or_, (Q(center_name__icontains=item) for item in filter_item if item)))
            if filters.get('region'):
                filter_item = filters.get('region')
                if len(filter_item) == 1:
                    centers = centers.filter(region__icontains=filter_item[0])
                else:
                    centers = centers.filter(reduce(operator.or_, (Q(region__icontains=item) for item in filter_item if item)))
            if filters.get('district'):
                filter_item = filters.get('district')
                if len(filter_item) == 1:
                    centers = centers.filter(district__icontains=filter_item[0])
                else:
                    centers = centers.filter(reduce(operator.or_, (Q(district__icontains=item) for item in filter_item if item)))

        num = centers.count()

        if pagination:
            paginator = Paginator(centers, page_size,)
            current_page = int(offset/page_size) + 1
            centers = paginator.page(current_page).object_list

        centers_id_list = centers.values_list('center_id', flat=True)

        centers_record = pd.DataFrame.from_records(centers.values(
                                                           'center_id',
                                                           'center_name',
                                                           'region',
                                                           'district',
                                                           ))

        if centers_record.empty:

            return pd.DataFrame(), 0

        # Start to calculate league statistics

        leagueObjs = LeagueFood.objects \
            .filter(
                centerId__in=centers_id_list,
                openDate__gte=start,
                openDate__lte=end
            )

        leagueRecords = pd.DataFrame.from_records(leagueObjs.values('centerId',
                                                                    'revenueAmount'
                                                                    ))

        if leagueRecords.empty:
            return pd.DataFrame(), num

        leagueRecords = pd.pivot_table(leagueRecords,
                                       index=['centerId'],
                                       values=['revenueAmount'],
                                       aggfunc='sum'
                                       )

        leagueRecords.reset_index(inplace=True)

        leagueRecords.rename({'revenueAmount': 'revenue_food',
                              'centerId': 'center_id'
                              }, axis=1, inplace=True)

        leagueRecords['center_id'] = leagueRecords['center_id'].astype(int)
        leagueRecords = leagueRecords.where((pd.notnull(leagueRecords)), None)

        return leagueRecords, num

    @classmethod
    def get_center_info_alcohol(cls, start, end, type_, subType, dow, dowRange, dateRange, status, distinct,
                        pagination=False, page_size=None, offset=None, filters=None, sort=None, order=None):

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
                    centers = centers.filter(reduce(operator.or_, (Q(center_name__icontains=item) for item in filter_item if item)))
            if filters.get('region'):
                filter_item = filters.get('region')
                if len(filter_item) == 1:
                    centers = centers.filter(region__icontains=filter_item[0])
                else:
                    centers = centers.filter(reduce(operator.or_, (Q(region__icontains=item) for item in filter_item if item)))
            if filters.get('district'):
                filter_item = filters.get('district')
                if len(filter_item) == 1:
                    centers = centers.filter(district__icontains=filter_item[0])
                else:
                    centers = centers.filter(reduce(operator.or_, (Q(district__icontains=item) for item in filter_item if item)))

        num = centers.count()

        if pagination:
            paginator = Paginator(centers, page_size,)
            current_page = int(offset/page_size) + 1
            centers = paginator.page(current_page).object_list

        centers_id_list = centers.values_list('center_id', flat=True)

        centers_record = pd.DataFrame.from_records(centers.values(
                                                           'center_id',
                                                           'center_name',
                                                           'region',
                                                           'district',
                                                           ))

        if centers_record.empty:

            return pd.DataFrame(), 0

        # Start to calculate league statistics

        leagueObjs = LeagueAlocohol.objects \
            .filter(
                centerId__in=centers_id_list,
                openDate__gte=start,
                openDate__lte=end
            )

        leagueRecords = pd.DataFrame.from_records(leagueObjs.values('centerId',
                                                                    'revenueAmount'
                                                                    ))

        if leagueRecords.empty:
            return pd.DataFrame(), num

        leagueRecords = pd.pivot_table(leagueRecords,
                                       index=['centerId'],
                                       values=['revenueAmount'],
                                       aggfunc='sum'
                                       )

        leagueRecords.reset_index(inplace=True)

        leagueRecords.rename({'revenueAmount': 'revenue_alcohol',
                              'centerId': 'center_id'
                              }, axis=1, inplace=True)

        leagueRecords['center_id'] = leagueRecords['center_id'].astype(int)
        leagueRecords = leagueRecords.where((pd.notnull(leagueRecords)), None)

        return leagueRecords, num
