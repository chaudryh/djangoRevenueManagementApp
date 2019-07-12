import pandas as pd
import openpyxl
import os

from ..models.models import *


class LoadConfigData:

    def __init__(self, file=None, workers_sheet='workers', companies_sheet='companies', AOR_sheet='AOR'):

        self.workers_sheet = workers_sheet
        self.companies_sheet = companies_sheet
        self.AOR_sheet = AOR_sheet

        if file:
            self.file = file
        if not file:
            self.file = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'sample/ConfigData.xlsx')

    def load_worker(self):
        data = pd.read_excel(self.file, self.workers_sheet)
        for index, row in data.iterrows():
            company = Company.objects.get(business_name__exact=row['company'])
            Workers.objects.update_or_create(id=row['id'],
                                             defaults={
                                                'name': row['name'],
                                                'last_name': row['last_name'],
                                                'first_name': row['first_name'],
                                                'company': company,
                                                'level': row['level'],
                                                'shift': row['shift'],
                                                'type': row['type']
                                             })

    def load_company(self):
        data = pd.read_excel(self.file, self.companies_sheet)
        for index, row in data.iterrows():
            Company.objects.update_or_create(id=row['id'],
                                             defaults={
                                                 'business_name': row['business_name'],
                                                 'address': row['address']
                                             })

    def load_aor(self):
        data = pd.read_excel(self.file, self.AOR_sheet)
        for index, row in data.iterrows():
            worker = Workers.objects.get(name__exact=row['worker'].upper())
            AOR.objects.update_or_create(id=row['id'],
                                         defaults={
                                             'worker': worker,
                                             'line': row['line'],
                                             'AOR_type': row['type'],
                                             'equip_name': row['equip name'],
                                             'equip_code': row['equip code'],
                                         })

    def load(self):

        self.load_company()
        self.load_worker()
        self.load_aor()


if __name__ == "__main__":

    LoadConfigData().load_aor()
