from bowlero_backend.celery import app
import os

from Celery.RollOver.BowlingRollOver import BowlingRollOver
from Celery.RollOver.ShoeRollOver import ShoeRollOver
from Celery.RollOver.ProductRollOver import ProductRollOver
from Celery.RollOver.MomentFeedRollOver import MomentFeedRollOver

from api.AcisAPI import AcisAPI
from Email.EmailNotice.EmailNotice import EmailNotice


@app.task
def roll_over_retail_bowling():
    BowlingRollOver.retail_bowling_roll_over()

    return


@app.task
def roll_over_retail_shoe():
    ShoeRollOver.retail_shoe_roll_over()

    return


@app.task
def roll_over_product():
    ProductRollOver.product_roll_over()

    return


@app.task
def roll_over_momentfeed():
    try:
        MomentFeedRollOver.momentfeed_roll_over()
    except Exception as e:
        # Send out notice
        subject = 'Moment feed pull failed'
        html_content = '''
            {error}
        '''.format(error=e)

        to_emails = ['atu@bowlerocorp.com']
        EmailNotice.send_emails(subject, html_content, to_emails=to_emails)

    return


@app.task
def roll_over_weather():
    AcisAPI.sync_points_weather()

    return


@app.task
def email_notice():
    EmailNotice.emails_calendar_events()

    return
