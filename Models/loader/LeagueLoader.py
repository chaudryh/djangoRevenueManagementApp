import os
import sys
import numpy as np
import pandas as pd
import re
from datetime import datetime as dt, timedelta as td
import pytz
import time
import math

# sys.path.append('../..')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'bowlero_backend.settings'
django.setup()

from bowlero_backend.settings import TIME_ZONE, BASE_DIR
from django.http import JsonResponse

from RM.Centers.models.models import *
from RM.Pricing.models.models import *
from Models.models.models import *

from utils.UDatetime import UDatetime

from DAO.DataDAO import *

EST = pytz.timezone(TIME_ZONE)


class LeagueLoader:

    @classmethod
    def league_loader(cls):
        League.objects.all().delete()
        file_path = os.path.join(BASE_DIR, 'Models/loader/files/TestLeagueExtractSample.xlsx')
        records = pd.read_excel(file_path)
        records = records.where((pd.notnull(records)), None)

        records['start'] = records[['StartDate', 'StartTime']] \
            .apply(lambda x: dt(x['StartDate'].year, x['StartDate'].month, x['StartDate'].day,
                                x['StartTime'].hour, x['StartTime'].minute, x['StartTime'].second,
                                tzinfo=pytz.UTC
                                ), axis=1)

        records['end'] = records[['EndDate', 'EndTime']] \
            .apply(lambda x: dt(x['EndDate'].year, x['EndDate'].month, x['EndDate'].day,
                                x['EndTime'].hour, x['EndTime'].minute, x['EndTime'].second,
                                tzinfo=pytz.UTC
                                ), axis=1)

        for index, row in records.iterrows():
            try:
                center_obj = Centers.objects.get(center_id=row['CenterNumber'])
            except Exception:
                continue

            League.objects.create(
                leagueId=row['LeagueId'],
                leagueIdCopied=row['CopiedFromLeagueId'],
                centerId=center_obj,
                leagueName=row['LeagueName'],
                leagueType=row['LeagueType'],
                leagueSubType=row['LeagueSubType'],
                leagueStatus=row['LeagueStatus'],
                dayOfWeekName=row['DayOfWeekName'],
                daysPerWeek=row['DaysPerWeek'],
                numberOfWeeks=row['NumberOfWeeks'],
                start=row['start'],
                end=row['end'],
                startingLaneNumber=row['StartingLaneNumber'],
                endingLaneNumber=row['EndingLaneNumber'],
                bowlerEquivalentGoal=row['BowlerEquivalentGoal'],
                confirmedBowlerCount=row['ConfirmedBowlerCount'],
                currentYearLeagueNumber=row['CurrentYearLeagueNumber'],
                playersPerTeam=row['PlayersPerTeam'],
                numberOfTeams=row['NumberOfTeams'],
                gamesPerPlayer=row['GamesPerPlayer'],
                lineageCost=round(float(row['LineageCost']), 2),
            )

    @classmethod
    def league_last_update(cls):

        data = pd.DataFrame.from_records(League.objects.all().values())
        data = data[~data['leagueId'].isin(data['leagueIdCopied'])]

        # data_new = data[~data['leagueIdCopied'].isnull()]
        # data_new = data_new[~data_new['leagueIdCopied'].isin(data['LeagueId'])]

        for index, row in data.iterrows():
            leagueId = row['leagueId']
            League.objects.filter(leagueId=leagueId).update(last=True)

    @classmethod
    def league_column_update(cls):
        file_path = os.path.join(BASE_DIR, 'Models/loader/files/LeagueTestExtract_20190226.xlsx')
        records = pd.read_excel(file_path)
        records = records.where((pd.notnull(records)), None)

        for index, row in records.iterrows():
            try:
                center_obj = Centers.objects.get(center_id=row['CenterNumber'])
            except Exception:
                continue

            League.objects \
                .filter(leagueId=row['LeagueId']) \
                .update(leagueFrequency=row['LeagueFrequency'])


if __name__ == "__main__":
    loader = input('Please give the loader type('
                   '1:load league;'
                   '2:update last field;'
                   '3:update league field'
                   '):')
    if int(loader) == 1:
        LeagueLoader.league_loader()
    elif int(loader) == 2:
        LeagueLoader.league_last_update()
    elif int(loader) == 3:
        LeagueLoader.league_column_update()


