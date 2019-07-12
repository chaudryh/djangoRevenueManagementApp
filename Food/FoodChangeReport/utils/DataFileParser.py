import pandas as pd
from ...WorkTasks.models import *


class DataExcelParser:

    def parse_data(self, file):

        data = pd.read_excel(file)

        return data

    def save2db(self, raw_data):
        pass