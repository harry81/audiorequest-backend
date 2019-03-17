import boto3
from django.conf import settings


def send_email(from_address=settings.DEFAULT_EMAIL_ADDRESS, to_addresses=[settings.DEFAULT_EMAIL_ADDRESS],
               subject='stt test', text='body', html='html'):
    ses = boto3.client('ses', 'us-east-1')

    response = ses.send_email(
        Destination={
            'ToAddresses': to_addresses,
            'BccAddresses': [settings.DEFAULT_EMAIL_ADDRESS],
        },
        Message={
            'Body': {
                'Html': {
                    'Charset': 'UTF-8',
                    'Data': html,
                },
                'Text': {
                    'Charset': 'UTF-8',
                    'Data': text,
                },
            },
            'Subject': {
                'Charset': 'UTF-8',
                'Data': subject,
            },
        },
        Source=from_address,
    )
    print('Sent email to %s | %s' % (to_addresses, response))
