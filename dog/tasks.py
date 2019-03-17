from datetime import datetime

import boto3
from dateutil.relativedelta import relativedelta

from .utils import send_email

client = boto3.client('ce', region_name='ap-northeast-2')


def daily_report():
    response = client.get_cost_and_usage(
        TimePeriod={
            'Start': datetime.strftime(datetime.now(), "%Y-%m-01"),
            'End': datetime.strftime(datetime.today() + relativedelta(months=1), "%Y-%m-01")
        },
        Granularity='MONTHLY',
        Metrics=[
            'AmortizedCost',
        ]
    )
    res = dict(
        start=response['ResultsByTime'][0]['TimePeriod']['Start'],
        end=response['ResultsByTime'][0]['TimePeriod']['End'],
        amount=response['ResultsByTime'][0]['Total']['AmortizedCost']['Amount'][:4],
        unit=response['ResultsByTime'][0]['Total']['AmortizedCost']['Unit']
    )

    text = "{start} ~ {end} : {amount} {unit}".format(**res)
    send_email(subject='AWS uasges {amount}'.format(**res), html=text)
