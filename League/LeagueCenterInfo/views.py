import os
import numpy as np
import pandas as pd
import re
from datetime import datetime as dt, timedelta
import pytz
import time

from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse

from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_protect, csrf_exempt

from bowlero_backend.settings import TIME_ZONE, BASE_DIR
from .models.models import *

from DAO.DataDAO import *
from DAO.LeagueDataDAO import *


# Create your views here.
# from .utils.LoadConfigData import LoadConfigData

EST = pytz.timezone(TIME_ZONE)


@staff_member_required(login_url='/login/')
@csrf_protect
def index(request, *args, **kwargs):
    template_name = 'LeagueCenterInfo/LeagueCenterInfoIndex.html'
    return render(request, template_name)


class Panel1:
    class Form1:

        # result_path = os.path.join(BASE_DIR, 'media/RM/Centers/centers.xlsx')

        @classmethod
        def submit(cls, request, *args, **kwargs):

            response = Panel2.Table1.get_columns(request, *args, **kwargs)

            return response

        @classmethod
        def fileupload(cls, request, *args, **kwargs):
            files = request.FILES.getlist('FileUpload')

            file_path = os.path.join(BASE_DIR, 'media/RM/Centers/centers.xlsx')

            if request.method == 'POST' and files:
                for file in files:
                    data = pd.read_excel(file)
                    data.to_excel(file_path)

            return JsonResponse({})


class Panel2:
    class Table1:

        @staticmethod
        def get_columns(request, *args, **kwargs):
            columns = \
                [
                    {
                        'field': 'center_id', 'title': 'Center', 'sortable': False, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'},
                        'class': 'fixed-column-center'
                    },
                    {
                        'field': 'center_name', 'title': 'Center Name', 'sortable': False, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'},
                        'class': 'fixed-column-center-name'
                    },
                    {
                        'field': 'region', 'title': 'Region', 'sortable': False, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'},
                        'class': 'fixed-column-region'
                    },
                    {
                        'field': 'district', 'title': 'District', 'sortable': False, 'editable': False,
                        'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'},
                        'class': 'fixed-column-district'
                    },
                    {
                        'field': 'totalLMA', 'title': 'Total LMA', 'sortable': False, 'editable': False,
                        'align': 'center', 'vlign': 'center',
                        'class': 'fixed-column-total-LMA'
                    },
                    {
                        'field': 'totalPixel', 'title': 'Total Pixel', 'sortable': False, 'editable': False,
                        'align': 'center', 'vlign': 'center',
                        'class': 'fixed-column-total-Pixel'
                    },
                    {
                        'field': 'revenue', 'title': 'Rev LMA', 'sortable': False, 'editable': False,
                        'align': 'center', 'vlign': 'center',
                        'class': 'fixed-column-revenue'
                    },
                    {
                        'field': 'revenue_transact', 'title': 'Rev Pixel', 'sortable': False, 'editable': False,
                        'align': 'center', 'vlign': 'center',
                        'class': 'fixed-column-revenue-transact'
                    },
                    {
                        'field': 'revenue_var', 'title': 'Rev Var', 'sortable': False, 'editable': False,
                        'align': 'center', 'vlign': 'center',
                        'class': 'fixed-column-revenue-var'
                    },
                    {
                        'field': 'weeklyValue', 'title': 'Wk. Rev LMA', 'sortable': False, 'editable': False,
                        'align': 'center', 'vlign': 'center',
                        'class': 'fixed-column-weeklyValue'
                    },
                    {
                        'field': 'revenue_transact_weekly', 'title': 'Wk. Rev Pixel', 'sortable': False,
                        'editable': False,
                        'align': 'center', 'vlign': 'center',
                        'class': 'fixed-column-revenue-transact-weekly'
                    },
                    {
                        'field': 'revenue_weekly_var', 'title': 'Wk. Rev Var', 'sortable': False, 'editable': False,
                        'align': 'center', 'vlign': 'center',
                        'class': 'fixed-column-revenue-var-weekly'
                    },
                    {
                        'field': 'seasonalValue', 'title': 'Seas. Rev LMA', 'sortable': False, 'editable': False,
                        'align': 'center', 'vlign': 'center',
                        'class': 'fixed-column-seasonalValue'
                    },
                    {
                        'field': 'revenue_transact_seasonal', 'title': 'Seas. Rev Pixel', 'sortable': False,
                        'editable': False,
                        'align': 'center', 'vlign': 'center',
                        'class': 'fixed-column-revenue-transact-seasonal'
                    },
                    {
                        'field': 'revenue_seasonal_var', 'title': 'Seas. Rev Var', 'sortable': False, 'editable': False,
                        'align': 'center', 'vlign': 'center',
                        'class': 'fixed-column-revenue-var-seasonal'
                    },
                    {
                        'field': 'avgWeeklyValue', 'title': 'Avg Weekly Value', 'sortable': False, 'editable': False,
                        'align': 'center', 'vlign': 'center',
                    },
                    {
                        'field': 'avgSeasonalValue', 'title': 'Avg Seasonal Value', 'sortable': False,
                        'editable': False, 'align': 'center', 'vlign': 'center',
                    },
                    {
                        'field': 'revenue_food', 'title': 'Revenue Food', 'sortable': False, 'editable': False,
                        'align': 'center', 'vlign': 'center',
                    },
                    {
                        'field': 'revenue_alcohol', 'title': 'Revenue Alcohol', 'sortable': False, 'editable': False,
                        'align': 'center', 'vlign': 'center',
                    },
                    {
                        'field': 'revenue_alcohol_per', 'title': 'Other', 'sortable': False, 'editable': True,
                        'align': 'center', 'vlign': 'center',
                    },
                    {
                        'field': 'minWeeks', 'title': 'Min Weeks', 'sortable': False, 'editable': False,
                        'align': 'center', 'vlign': 'center',
                    },
                    {
                        'field': 'maxWeeks', 'title': 'Max Weeks', 'sortable': False, 'editable': False,
                        'align': 'center', 'vlign': 'center',
                    },
                    {
                        'field': 'avgPlayersPerTeam', 'title': 'Avg Players/Team', 'sortable': False, 'editable': False,
                        'align': 'center', 'vlign': 'center',
                    },
                    {
                        'field': 'avgPlayersPerLeague', 'title': 'Avg Players / League', 'sortable': False, 'editable': False,
                        'align': 'center', 'vlign': 'center',
                    },
                    {
                        'field': 'avgTeamsPerLeague', 'title': 'Avg Teams / League', 'sortable': False, 'editable': False,
                        'align': 'center', 'vlign': 'center',
                    },
                    {
                        'field': 'avgGamesPerBowler', 'title': 'Avg Games / Bowler', 'sortable': False, 'editable': False,
                        'align': 'center', 'vlign': 'center',
                    },
                    {
                        'field': 'avgGamesPerLeague', 'title': 'Avg Games / League', 'sortable': False, 'editable': False,
                        'align': 'center', 'vlign': 'center',
                    },
                    {
                        'field': 'avgLineagePerLeague', 'title': 'Avg Lineage$ / League', 'sortable': False, 'editable': False,
                        'align': 'center', 'vlign': 'center',
                    },
                    {
                        'field': 'avgLineagePerGame', 'title': 'Avg Price$ / Game', 'sortable': False, 'editable': False,
                        'align': 'center', 'vlign': 'center',
                    },
                    {
                        'field': 'avgLineagePerBowler', 'title': 'Avg Lineage$ / Bowler', 'sortable': False, 'editable': False,
                        'align': 'center', 'vlign': 'center',
                    },
                    {
                        'field': 'confirmedBowler', 'title': 'Confirmed Bowler', 'sortable': False, 'editable': False,
                        'align': 'center', 'vlign': 'center',
                    },
                    {
                        'field': 'leagueCount', 'title': 'League Count', 'sortable': False, 'editable': False,
                        'align': 'center', 'vlign': 'center',
                    },
                    # {
                    #     'field': 'cover_month', 'title': 'League Months', 'sortable': False, 'editable': False,
                    #     'align': 'center', 'vlign': 'center',
                    # },
                    # {
                    #     'field': 'cover_dow', 'title': 'Day of Week', 'sortable': False, 'editable': False,
                    #     'align': 'center', 'vlign': 'center',
                    # },
                    # {
                    #     'field': 'max_cover', 'title': 'Max Cover', 'sortable': False, 'editable': False,
                    #     'align': 'center', 'vlign': 'center',
                    # },
                    # {
                    #     'field': 'avg_lineage_cost', 'title': 'Avg Lineage Cost', 'sortable': False, 'editable': False,
                    #     'align': 'center', 'vlign': 'center',
                    # },
                    # {
                    #     'field': 'share_of_PF_bowlero', 'title': 'Avg Cost of Acquisition', 'sortable': False, 'editable': False,
                    #     'align': 'center', 'vlign': 'center',
                    # },
                    # {
                    #     'field': 'avg_Bowlero_share_of_PF', 'title': 'Avg Bowlero share of PF', 'sortable': False, 'editable': False,
                    #     'align': 'center', 'vlign': 'center',
                    # },
                    # {
                    #     'field': 'avg_treasurer_share_of_PF', 'title': 'Avg Treasurer Share of PF', 'sortable': False, 'editable': False,
                    #     'align': 'center', 'vlign': 'center',
                    # },
                ]

            return JsonResponse({'status': 1, 'msg': '', 'columns': columns})

        @staticmethod
        def get_columns_details(request, *args, **kwargs):

            columns = \
            [
                {
                    'field': 'centerId', 'title': 'Center', 'sortable': False, 'editable': False,
                    'align': 'center', 'vlign': 'center',
                    'class': 'fixed-column-center'
                },
                {
                    'field': 'currentYearLeagueNumber', 'title': 'League No.', 'sortable': False, 'editable': False,
                    'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'},
                    'class': 'fixed-column-league-number'
                },
                {
                    'field': 'leagueName', 'title': 'League Name', 'sortable': False, 'editable': False,
                    'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'},
                    'class': 'fixed-column-league-name'
                },
                {
                    'field': 'start', 'title': 'Start Date', 'sortable': False, 'editable': False,
                    'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'},
                    'class': 'fixed-column-start'
                },
                {
                    'field': 'end', 'title': 'End Date', 'sortable': False, 'editable': False,
                    'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'},
                    'class': 'fixed-column-end'
                },
                {
                    'field': 'revenue', 'title': 'Rev LMA', 'sortable': False, 'editable': False,
                    'align': 'center', 'vlign': 'center',
                    'class': 'fixed-column-revenue'
                },
                {
                    'field': 'revenue_transact', 'title': 'Rev Pixel', 'sortable': False, 'editable': False,
                    'align': 'center', 'vlign': 'center',
                    'class': 'fixed-column-revenue-transact'
                },
                {
                    'field': 'revenue_var', 'title': 'Rev Var', 'sortable': False, 'editable': False,
                    'align': 'center', 'vlign': 'center',
                    'class': 'fixed-column-revenue-var'
                },
                {
                    'field': 'weeklyValue', 'title': 'Wk. Rev LMA', 'sortable': False, 'editable': False,
                    'align': 'center', 'vlign': 'center',
                    'class': 'fixed-column-weeklyValue'
                },
                {
                    'field': 'revenue_transact_weekly', 'title': 'Wk. Rev Pixel', 'sortable': False,
                    'editable': False,
                    'align': 'center', 'vlign': 'center',
                    'class': 'fixed-column-revenue-transact-weekly'
                },
                {
                    'field': 'revenue_weekly_var', 'title': 'Wk. Rev Var', 'sortable': False, 'editable': False,
                    'align': 'center', 'vlign': 'center',
                    'class': 'fixed-column-revenue-var-weekly'
                },
                {
                    'field': 'seasonalValue', 'title': 'Seas. Rev LMA', 'sortable': False, 'editable': False,
                    'align': 'center', 'vlign': 'center',
                    'class': 'fixed-column-seasonalValue'
                },
                {
                    'field': 'revenue_transact_seasonal', 'title': 'Seas. Rev Pixel', 'sortable': False,
                    'editable': False,
                    'align': 'center', 'vlign': 'center',
                    'class': 'fixed-column-revenue-transact-seasonal'
                },
                {
                    'field': 'revenue_seasonal_var', 'title': 'Seas. Rev Var', 'sortable': False, 'editable': False,
                    'align': 'center', 'vlign': 'center',
                    'class': 'fixed-column-revenue-var-seasonal'
                },
                {
                    'field': 'lineageCost', 'title': 'Lineage$', 'sortable': False, 'editable': False,
                    'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                },
                {
                    'field': 'leagueFrequency', 'title': 'Frequency', 'sortable': False,
                    'editable': False,
                    'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                },
                {
                    'field': 'dayOfWeekName', 'title': 'DOW', 'sortable': False,
                    'editable': False,
                    'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                },
                {
                    'field': 'numberOfWeeks', 'title': 'Weeks', 'sortable': False, 'editable': False,
                    'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                },
                {
                    'field': 'lanes', 'title': 'Lanes', 'sortable': False,
                    'editable': False,
                    'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                },
                {
                    'field': 'startingLaneNumber', 'title': 'Start Lane No.', 'sortable': False, 'editable': False,
                    'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                },
                {
                    'field': 'endingLaneNumber', 'title': 'End Lane No.', 'sortable': False, 'editable': False,
                    'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                },
                {
                    'field': 'bowlerEquivalentGoal', 'title': 'Bowler Equivalent Goal', 'sortable': False, 'editable': False,
                    'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                },
                {
                    'field': 'confirmedBowlerCount', 'title': 'Confirmed Bowler Count', 'sortable': False, 'editable': False,
                    'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                },
                {
                    'field': 'playersPerTeam', 'title': 'Players/Team', 'sortable': False, 'editable': False,
                    'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                },
                {
                    'field': 'numberOfTeams', 'title': 'Number Of Teams', 'sortable': False,
                    'editable': False,
                    'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                },
                {
                    'field': 'gamesPerPlayer', 'title': 'Games/Player', 'sortable': False, 'editable': False,
                    'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                },
                {
                    'field': 'leagueId', 'title': 'League Id', 'sortable': False, 'editable': False,
                    'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                },
                {
                    'field': 'leagueIdCopied', 'title': 'League Id Copied', 'sortable': False, 'editable': False,
                    'align': 'center', 'vlign': 'center', 'filter': {'type': 'input'}
                },
            ]

            return JsonResponse({'status': 1, 'msg': '', 'columns': columns})

        @staticmethod
        def create(request, *args, **kwargs):
            page_size = int(request.GET.get('limit'))
            offset = int(request.GET.get('offset'))
            filters = request.GET.get('filter')
            sort = request.GET.get('sort')
            order = request.GET.get('order')

            start = request.GET.get('start')
            end = request.GET.get('end')
            type_ = request.GET.getlist('type[]')
            subType = request.GET.getlist('subType[]')
            dow = request.GET.getlist('dow[]')
            dowRange = request.GET.get('dowRange')
            dateRange = request.GET.get('dateRange')
            status = request.GET.getlist('status[]')
            distinct = request.GET.get('distinct')

            dowRange = dateRange

            # Formatting Data
            start = UDatetime.datetime_str_init(start).date() if start else None
            end = UDatetime.datetime_str_init(end).date() if end else None
            distinct = True if distinct == 'True' else False

            # Find if all in the selections
            type_ = [] if type_ and 'all' in type_ else type_
            subType = [] if subType and 'all' in subType else subType
            dow = [] if dow and 'all' in dow else dow
            status = [] if status and 'all' in status else status

            # Remove empty string
            type_ = [item for item in type_ if item]
            subType = [item for item in subType if item]
            dow = [item for item in dow if item]
            status = [item for item in status if item]

            if dateRange == 'happen':
                data, num = LeagueDataDao.get_center_info_happen(
                    start, end, type_, subType, dow, dowRange, dateRange, status, distinct,
                    pagination=True,
                    page_size=page_size,
                    offset=offset,
                    filters=filters,
                    sort=sort,
                    order=order,
                )
            else:
                data, num = LeagueDataDao.get_center_info(
                                             start, end, type_, subType, dow, dowRange, dateRange, status, distinct,
                                             pagination=True,
                                             page_size=page_size,
                                             offset=offset,
                                             filters=filters,
                                             sort=sort,
                                             order=order,
                                             )

            # Join calculations from transaction table

            data_transact, num_transact = LeagueDataDao.get_center_info_transact(
                                             start, end, type_, subType, dow, dowRange, dateRange, status, distinct,
                                             pagination=True,
                                             page_size=page_size,
                                             offset=offset,
                                             filters=filters,
                                             sort=sort,
                                             order=order,
                                             )

            if not data_transact.empty:
                data = data.join(data_transact.set_index(['center_id']), on=['center_id'], how='left')
            else:
                data['revenue_transact'] = None
                data['revenue_transact_weekly'] = None
                data['revenue_transact_seasonal'] = None

            # Join calculations from food table
            data_food, num_food = LeagueDataDao.get_center_info_food(
                                             start, end, type_, subType, dow, dowRange, dateRange, status, distinct,
                                             pagination=True,
                                             page_size=page_size,
                                             offset=offset,
                                             filters=filters,
                                             sort=sort,
                                             order=order,
                                             )

            if not data_food.empty:
                data = data.join(data_food.set_index(['center_id']), on=['center_id'], how='left')
            else:
                data['revenue_food'] = None

            # Replace Food Rev with 0 for centers without league included
            data[data['revenue'] == None]['revenue_food'] = None

            # Join calculations from alcohol table
            data_alcohol, num_alcohol = LeagueDataDao.get_center_info_alcohol(
                                             start, end, type_, subType, dow, dowRange, dateRange, status, distinct,
                                             pagination=True,
                                             page_size=page_size,
                                             offset=offset,
                                             filters=filters,
                                             sort=sort,
                                             order=order,
                                             )

            if not data_alcohol.empty:
                data = data.join(data_alcohol.set_index(['center_id']), on=['center_id'], how='left')
            else:
                data['revenue_alcohol'] = None

            # Replace Alcohol Rev with 0 for centers without league included
            data[data['revenue'] == None]['revenue_alcohol'] = None

            # Add Other
            centers = Centers.objects.filter(center_id__in=data['center_id'].tolist())
            alcoholPer = pd.DataFrame.from_records(centers.values('center_id',
                                                                  'leagueAlcoholPer'))
            alcoholPer['center_id'] = alcoholPer['center_id'].astype(int)
            data = data.join(alcoholPer.set_index(['center_id']), on=['center_id'], how='left')
            data.rename({'leagueAlcoholPer': 'revenue_alcohol_per'}, axis=1, inplace=True)

            # Add total
            data = data.where((pd.notnull(data)), 0)
            data['totalLMA'] = data['revenue'] + data['revenue_food'] + data['revenue_alcohol'] + data['revenue_alcohol_per']
            data['totalPixel'] = data['revenue_transact'] + data['revenue_food'] + data['revenue_alcohol'] + data['revenue_alcohol_per']

            # Add var
            data['revenue_var'] = data['revenue'] - data['revenue_transact']
            data['revenue_weekly_var'] = data['weeklyValue'] - data['revenue_transact_weekly']
            data['revenue_seasonal_var'] = data['seasonalValue'] - data['revenue_transact_seasonal']

            # Monetarize
            moneyFieldsOnlyIntegar = [
                'weeklyValue', 'avgWeeklyValue', 'seasonalValue', 'avgSeasonalValue', 'revenue',
                'revenue_transact', 'revenue_transact_weekly', 'revenue_transact_seasonal',
                'revenue_food', 'revenue_alcohol',
                'totalLMA', 'totalPixel',
                'revenue_var', 'revenue_weekly_var', 'revenue_seasonal_var'
            ]
            moneyFieldsWithDecimal = ['avgLineagePerLeague', 'avgLineagePerGame', 'avgLineagePerBowler']

            for field in moneyFieldsOnlyIntegar:
                data[field] = data[field].apply(lambda x: format_decimal(x, u'$#,###') if x else None)

            for field in moneyFieldsWithDecimal:
                data[field] = data[field].apply(lambda x: format_currency(x, 'USD') if x else None)

            if not data.empty:
                data = data.where((pd.notnull(data)), '-')

                data_response = data.to_dict(orient='records')
                response = {
                    'total': num,
                    'rows': data_response
                }
            else:
                response = {
                    'total': 0,
                    'rows': []
                }
            return JsonResponse(response, safe=False)

        @staticmethod
        def edit(request, *args, **kwargs):
            id = request.GET.get('id')
            field = request.GET.get('field')
            center_id = request.GET.get('center_id')
            new_value = request.GET.get(field)
            old_value = request.GET.get('old_value')

            old_value = old_value.replace('$', '')
            new_value = new_value.replace('$', '')

            if not new_value:
                new_value = 0

            if field == 'revenue_alcohol_per':
                Centers.objects.filter(center_id=center_id).update(leagueAlcoholPer=new_value)

            return JsonResponse({})

        @staticmethod
        def create_details(request, *args, **kwargs):
            page_size = int(request.GET.get('limit'))
            offset = int(request.GET.get('offset'))
            filters = request.GET.get('filter')
            sort = request.GET.get('sort')
            order = request.GET.get('order')
            center_id = request.GET.get('center_id')

            start = request.GET.get('start')
            end = request.GET.get('end')
            type_ = request.GET.getlist('type[]')
            subType = request.GET.getlist('subType[]')
            dow = request.GET.getlist('dow[]')
            dowRange = request.GET.get('dowRange')
            dateRange = request.GET.get('dateRange')
            status = request.GET.getlist('status[]')
            distinct = request.GET.get('distinct')

            dowRange = dateRange

            # Formatting Data
            start = UDatetime.datetime_str_init(start).date() if start else None
            end = UDatetime.datetime_str_init(end).date() if end else None
            distinct = True if distinct == 'True' else False

            # Find if all in the selections
            type_ = [] if type_ and 'all' in type_ else type_
            subType = [] if subType and 'all' in subType else subType
            dow = [] if dow and 'all' in dow else dow
            status = [] if status and 'all' in status else status

            # Remove empty string
            type_ = [item for item in type_ if item]
            subType = [item for item in subType if item]
            dow = [item for item in dow if item]
            status = [item for item in status if item]

            if dateRange == 'happen':
                data, num = LeagueDataDao.get_center_info_detail_happen(
                    center_id, start, end, type_, subType, dow, dowRange, dateRange, status, distinct,
                    pagination=True,
                    page_size=page_size,
                    offset=offset,
                    filters=filters,
                    sort=sort,
                    order=order,
                )
            else:
                data, num = LeagueDataDao.get_center_info_detail(
                    center_id, start, end, type_, subType, dow, dowRange, dateRange, status, distinct,
                    pagination=True,
                    page_size=page_size,
                    offset=offset,
                    filters=filters,
                    sort=sort,
                    order=order,
                )

            # Join calculations from transaction table
            data_transact, num_transact = LeagueDataDao.get_center_info_transact_detail(
                                             center_id, start, end, type_, subType, dow, dowRange, dateRange, status, distinct,
                                             pagination=True,
                                             page_size=page_size,
                                             offset=offset,
                                             filters=filters,
                                             sort=sort,
                                             order=order,
                                             )

            if not data_transact.empty:
                data = data.join(data_transact.set_index(['leagueId']), on=['leagueId'], how='left')
            else:
                data['revenue_transact'] = None
                data['revenue_transact_weekly'] = None
                data['revenue_transact_seasonal'] = None

            # Add var
            data = data.where((pd.notnull(data)), 0)
            data['revenue_var'] = data['revenue'] - data['revenue_transact']
            data['revenue_weekly_var'] = data['weeklyValue'] - data['revenue_transact_weekly']
            data['revenue_seasonal_var'] = data['seasonalValue'] - data['revenue_transact_seasonal']

            # Monetarize
            moneyFieldsOnlyIntegar = [
                'weeklyValue', 'seasonalValue', 'revenue',
                'revenue_transact', 'revenue_transact_weekly', 'revenue_transact_seasonal',
                'revenue_var', 'revenue_weekly_var', 'revenue_seasonal_var'
            ]
            moneyFieldsWithDecimal = ['lineageCost']

            for field in moneyFieldsOnlyIntegar:
                data[field] = data[field].apply(lambda x: format_decimal(x, u'$#,###') if x else None)

            for field in moneyFieldsWithDecimal:
                data[field] = data[field].apply(lambda x: format_currency(x, 'USD') if x else None)

            if not data.empty:
                data = data.where((pd.notnull(data)), "-")

                data_response = data.to_dict(orient='records')
                response = {
                    'total': num,
                    'rows': data_response
                }
            else:
                response = {
                    'total': 0,
                    'rows': []
                }

            return JsonResponse(response, safe=False)


# Center
# Center Name
# Region
# District
# Min Weeks Bowled
# Max Weeks Bowled
# Busiest During (which time period of the year)
# Most Frequently Booked Day of Week
# Max number of Games Bowled by any League (Cover)
# Average Lineage Fee
# Average Cost of Acquisition (Retention/KB)
# Average Bowlero's share of PF
# Average Treasurer/Secretary Share of PF

# List All PLinks
# List All League Ids
# List All centaman_league_number
# League Names
# All Day of Week

# xxi.      No. of Bowlers on a Team (we calculate the Avg Number of Players) ?/Team or /League; sum(n)/n or sum(bowler/team * team) / sum(team) or sum(confirmed)/sum(team)
# xxii.      Number of Teams  in that League (we calculate the Avg) ? Avg Team/League sum(team)/sum(league)
# xxiii.      Number of Games per Bowler (We calculate the Avg) ? Games/Bowler sum(n)/n or sum(confirmed * Games)/sum(confirmed)
# xxiv.      Lineage Fee (we calculate the avg) sum(n)/n or (fee * games)/sum(games)
# xxv.      Calculate Average Lineage per Game ?
# xxvi.      Calculate the Weekly Value ?
# xxvii.      Calculate the Seasonal Value ?

#D Min week = min(NumberOfWeeks) = min(36,12,10)=10
#D Max week = max(NumberOfWeeks) = max(36,12,10)=36
# Avg Players/Team = sum(confirmed)/sum(team) = (40+30+16)/(10+8+6)=3.58
# Avg Players/League = sum(confirmed)/count(league) = (40+30+16)/3=28.7
# Avg Teams/League = sum(team)/count(league) = (10+8+6)/3=8
# Avg Games/Bowler = sum(confirmed * GamesPerPlayer)/sum(confirmed) = (40*5+30*4+16*3)/(40+30+16)=4.28
# Avg Games/League = sum(confirmed * GamesPerPlayer)/count(league) = (40*5+30*4+16*3)/3=122.7
# Avg Lineage$/League = sum(LineageCost)/count(league) = (10+12+13)/3=11.7
# Avg Lineage$/Game = sum(LineageCost)/sum(GamesPerPlayer) = (10+12+13)/(5+4+3)=2.9
# Avg Lineage$/Bowler = sum(LineageCost*confirmed)/sum(confirmed) = (10*40+12*30+13*16)/(40+30+16)=11.3
# Weekly Value (By Center) = sum(DaysPerWeek * LineageCost * confirmed) = 3*10*40+1*12*30+2*13*16 = $1976
#D Weekly Value (By League) = DaysPerWeek * LineageCost * confirmed = 3*10*40= $1200
# Avg Weekly Value = sum(DaysPerWeek * LineageCost * confirmed)/count(league) = (3*10*40+1*12*30+2*13*16)/3 = $658.7
# Seasonal Value (By Center) = sum(NumberOfWeeks * DaysPerWeek * LineageCost * confirmed) = 36*3*10*40+12*1*12*30+10*2*13*16 = $51680
#D Seasonal Value (By League) = NumberOfWeeks * DaysPerWeek * LineageCost * confirmed = 36*3*10*40 = $43200
# Avg Seasonal Value = sum(NumberOfWeeks * DaysPerWeek * LineageCost * confirmed)/count(league) = (36*3*10*40+12*1*12*30+10*2*13*16)/3 = $17226.7
