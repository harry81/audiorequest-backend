import os

import boto3
from django.conf import settings

from google.cloud import speech_v1p1beta1 as speech
from google.cloud.speech_v1p1beta1 import enums, types

GAC_PATH = 'google_application/feisty-bindery-117412-c4cf0e8c8240.json'
client = speech.SpeechClient()


def download_GAC():

    if not os.path.exists(settings.GAC_FILENAME):
        s3 = boto3.resource('s3', 'us-east-1')
        s3.Bucket('hmapps').download_file(GAC_PATH, settings.GAC_FILENAME)


def transcribe(filename=None):

    encoding = "LINEAR16" if filename.endswith('wav') else "FLAC"
    sample_rate_hertz = 44100 if filename.endswith('wav') else 16000

    config = types.RecognitionConfig(
        encoding=getattr(enums.RecognitionConfig.AudioEncoding, encoding),
        sample_rate_hertz=sample_rate_hertz,
        enable_separate_recognition_per_channel=True,
        audio_channel_count=1,
        language_code='ko-KR')

    audio = types.RecognitionAudio(uri='gs://pointer-bucket/%s' % filename)

    response = client.long_running_recognize(config, audio)

    print('Waiting for operation to complete...')
    response = response.result(timeout=90)

    return response


def send_email(from_address='chharry@gmail.com',
               to_addresses=['chharry@gmail.com'],
               subject='stt test', text='body', html='html'):
    ses = boto3.client('ses', 'us-east-1')

    response = ses.send_email(
        Destination={
            'ToAddresses': to_addresses,
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
