import os
import pandas as pd
from datetime import datetime as dt,timedelta
import pytz
from django.shortcuts import HttpResponse

class AdminToolTableManager:

    now = dt.now(tz=pytz.timezone('America/New_York'))

    @classmethod
    def SetData(cls,type,partner=None,property_id=None,as_of_date=dt(2017,4,17),StayDate=None,MarketCode=None,EntityId=None):
        from .DataVerification import DataVerification
        from processing.Requests import DataVerificationRequest
        from managers.ConfigurationManager import ConfigurationManager
        ConfigurationManager.initialize(
            "{0}/configuration/integration".format(os.path.dirname
                                                   (os.path.dirname
                                                    (os.path.dirname
                                                     (os.path.dirname
                                                      (os.path.dirname
                                                       (os.path.abspath(__file__))))))))

        request = DataVerificationRequest()

        if StayDate:
            StayDate = dt.strptime(StayDate,'%Y-%m-%d')
        else:
            StayDate = cls.now

        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'output/output.csv')
        request.file_path = output_path
        request.verification_type = type
        request.partner_code = partner
        request.property_id = property_id
        request.as_of_date = as_of_date
        request.stay_date = StayDate
        request.market_code = MarketCode
        request.entity_id = EntityId
        processor = DataVerification()
        result = processor.process(request)

        stream = open(output_path, 'w')
        try:
            stream.write(result.data)
        finally:
            stream.close()

        if type != 'reservation_trace':
            data = pd.read_csv(output_path)
            data.sort_values('Stay Date',inplace=True)
        else:
            return

        return data

class IngestorCheckManager:

    now = dt.now(tz=pytz.timezone('America/New_York'))
    start = str(now.date()- timedelta(days=1))
    end = str(now.date()+ timedelta(days=1))

    @classmethod
    def UpdateData(cls):

        from scripts.data_repair.Queues_add_fields.Queues_add_fields import Queues_add_fields
        try:
            Queues_add_fields(bound_type='inbound', StartDate=cls.start, EndDate=cls.end).execute()
            return {'status':1}
        except Exception as e:
            return {'status':0}

    @classmethod
    def SetData(cls,StartDate = None,EndDate = None):
        from scripts.data_analysis.Queues_analysis.Queues_analysis import queues_analysis
        if StartDate:
            start = StartDate
        else:
            start = cls.start

        if EndDate:
            end = EndDate
        else:
            end = cls.end

        results = queues_analysis(StartDate=start,EndDate=end).ResultsGroupByFull()
        return results
