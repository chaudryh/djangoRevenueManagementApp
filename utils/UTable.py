from utils.UDatetime import UDatetime
from datetime import datetime, timedelta

from configurations.config_models.models_choice import *


class UTable:

    @classmethod
    def create_columns(cls, columns_config_dict, rowspan=2):

        columns = []
        for column_config in columns_config_dict:
            pattern = \
            [
                {
                    'field': column_config['field'],
                    'title': column_config['title'],
                    'sortable': True,
                    'align': 'center',
                    'vlign': 'center',
                    'rowspan': rowspan,
                    'filter': {
                        'type': 'input'
                    }
                }
            ]
            columns += pattern

        return columns

    @classmethod
    def create_columns_by_date_range(cls, start, end, level=1):

        date_range = UDatetime.date_range(start, end)
        columns = []

        for date in date_range:
            if level == 1:
                dow = DOW_choice[date.weekday()][0]
                date_str = date.strftime('%Y%m%d')
                pattern = \
                [
                    {
                        'field': date_str,
                        'title': '{dow}<br/>{date}'.format(dow=dow.capitalize(), date=date.strftime('%Y-%m-%d')),
                        'colspan': 3,
                        'align': 'center'
                    }
                ]
            elif level == 2:
                date_str = date.strftime('%Y%m%d')
                pattern = \
                [
                    {
                        'field': '{date}-nonprime'.format(date=date_str),
                        'title': 'Non-Prime',
                        'sortable': True,
                        'editable': True,
                        'align': 'center'
                    },
                    {
                        'field': '{date}-prime'.format(date=date_str),
                        'title': 'Prime',
                        'sortable': True,
                        'editable': True,
                        'align': 'center'
                    },
                    {
                        'field': '{date}-premium'.format(date=date_str),
                        'title': 'Premium',
                        'sortable': True,
                        'editable': True,
                        'align': 'center'
                    }
                ]
            else:
                pattern = []

            columns += pattern

        return columns

