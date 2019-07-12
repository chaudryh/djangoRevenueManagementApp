import os
import sys
import requests

try:
    from bowlero_backend.ENV.env import ENV
except:
    ENV = 'LOCAL'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'bowlero_backend.settings'
django.setup()

from RM.Centers.models.models import *
from Email.EmailNotice.EmailNotice import EmailNotice


class ServerStatus:

    @classmethod
    def serverStatus(cls):
        webStatus = cls.webServerStatus()
        dbStatus = cls.dbServerStatus()
        celeryStatus = True

        status = {'webStatus': 'Good' if webStatus else 'Bad',
                  'dbStatus': 'Good' if dbStatus else 'Bad',
                  'celeryStatus': 'Good' if celeryStatus else 'Bad',
                  }

        cls.send_emails(status)

    @classmethod
    def webServerStatus(cls):
        url_dict = {
            'DEV': 'http://prod-ratewf01.na.amfbowl.net/',
            'PROD': 'http://dmz-ratewf01.na.amfbowl.net/'
        }
        url = url_dict[ENV]
        try:
            response = requests.get(url)
            response.raise_for_status()
            return True
        except Exception as e:
            return False

    @classmethod
    def dbServerStatus(cls):
        try:
            Centers.objects.first()
            return True
        except Exception as e:
            return False

    @classmethod
    def send_emails(cls, status):

        # Send out notice
        subject = 'RMS Servers Status Check'
        html_content = '''
            <h3>RMS Servers Status</h3>
            <p>Web Status: {webStatus}</p>
            <p>DB Status: {dbStatus}</p>
            <p>Celery Status: {celeryStatus}</p>
        '''.format(webStatus=status['webStatus'], dbStatus=status['dbStatus'], celeryStatus=status['celeryStatus'])

        to_emails = ['atu@bowlerocorp.com', 'jbagga@bowlerocorp.com']
        EmailNotice.send_emails(subject, html_content, to_emails=to_emails)

        return


if __name__ == '__main__':
    ServerStatus.serverStatus()

