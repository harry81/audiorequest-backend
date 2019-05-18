import logging
import os
import stat
import time

import boto3
from django.conf import settings

from google.api_core.exceptions import GoogleAPICallError, InvalidArgument
from google.cloud import speech_v1p1beta1 as speech
from google.cloud.speech_v1p1beta1 import enums, types

s3 = boto3.resource('s3', 'us-east-1')
s3_client = boto3.client('s3', 'us-east-1')
GAC_PATH = 'google_application/feisty-bindery-117412-c4cf0e8c8240.json'
client = speech.SpeechClient()
logger = logging.getLogger(__name__)


def download_GAC():
    print("### download_GAC")

    if not os.path.exists(settings.GAC_FILENAME):
        s3.Bucket('hmapps').download_file(GAC_PATH, settings.GAC_FILENAME)


def download_ffmpeg():
    print("### download ffmpeg")
    convert_path = settings.AUDIO_CONVERTER_PATH
    ffprobe_path = settings.AUDIO_FFPROBE_PATH

    if not os.path.exists('bin'):
        os.mkdir('bin')

    for ele in [convert_path, ffprobe_path]:
        if not os.path.exists(ele):
            s3.Bucket('hmapps').download_file(ele, ele)

            st = os.stat(ele)
            os.chmod(ele, st.st_mode | stat.S_IEXEC)
            logging.info("Copy file to %s" % ele)


def transcode(in_file, out_file=None):
    """
    Submit a job to transcode a file by its filename. The
    built-in web system preset is used for the single output.
    """
    # https://docs.aws.amazon.com/ko_kr/elastictranscoder/latest/developerguide/system-presets.html
    preset_id = '1351620000001-300200'  # WAV 44100Hz, 8비트
    preset_id = '1351620000001-300110'  # FLAC - CD
    preset_id = '1351620000001-300300'  # WAV 44100Hz, 16비트
    preset_id = '1550903637583-9how3u'  # WAV 44100Hz, 16비트 - auto
    preset_id = '1550903988892-zkx0b3'  # WAV 44100Hz, 16비트 - 1

    pipeline_id = '1550580586860-rguq7m'
    region_name = 'us-west-1'

    if not out_file:
        out_file = "%s.%s" % (in_file.split(".")[0], settings.AUDIO_EXT[0])

    transcoder = boto3.client('elastictranscoder', region_name)
    job = transcoder.create_job(
        PipelineId=pipeline_id,
        Input={
            'Key': in_file,
            'FrameRate': 'auto',
            'Resolution': 'auto',
            'AspectRatio': 'auto',
            'Interlaced': 'auto',
            'Container': 'auto'
        },
        Outputs=[{
            'Key': out_file,
            'PresetId': preset_id
        }]
    )

    for x in range(1, 6):
        logging.info('waint for the status..')
        job = transcoder.read_job(Id=job['Job']['Id'])
        print('wait for the status.. %s' % job['Job']['Status'])

        if job['Job']['Status'] == 'Error':
            raise Exception("%s [%s]" % (job['Job']['Output']['StatusDetail'], in_file))

        if job['Job']['Status'] not in ['Submitted', 'Progressing']:
            return job
        time.sleep(x * x)

    raise Exception('transcode')


def transcribe(filename=None, **kwargs):
    language = kwargs.get('language', 'ko-KR')
    channel = kwargs.get('channel', 1)
    # if the file is not in google storages, copy and keep going
    encoding = "LINEAR16" if filename.endswith('wav') else "FLAC"
    sample_rate_hertz = 44100  # if filename.endswith('wav') else 16000

    audio = types.RecognitionAudio(uri='gs://pointer-bucket/%s' % filename)

    # https://cloud.google.com/speech-to-text/docs/reference/rpc/google.cloud.speech.v1p1beta1
    config = types.RecognitionConfig(
        encoding=getattr(enums.RecognitionConfig.AudioEncoding, encoding),
        sample_rate_hertz=sample_rate_hertz, enable_separate_recognition_per_channel=True,
        enable_word_time_offsets=True,
        enable_automatic_punctuation=True,
        enable_speaker_diarization=True,
        model='default',
        alternative_language_codes=['en-US'],
        audio_channel_count=channel, language_code=language)

    try:
        response = client.long_running_recognize(config, audio)
    except InvalidArgument as e:
        message = "%s %s" % (e.args[0], audio)
        raise(Exception(message))

    print('Waiting for operation to complete...')
    try:
        response = response.result(timeout=90)
    except GoogleAPICallError as e:
        logger.error(e, filename)

    return response


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


def synthesize_text(text, language_code='en-US', filename='output.wav'):
    """Synthesizes speech from the input string of text."""
    from google.cloud import texttospeech
    client = texttospeech.TextToSpeechClient()

    input_text = texttospeech.types.SynthesisInput(text=text)

    # https://cloud.google.com/text-to-speech/docs/reference/rpc/google.cloud.texttospeech.v1beta1#google.cloud.texttospeech.v1beta1
    voice = texttospeech.types.VoiceSelectionParams(
        language_code=language_code,
        ssml_gender=texttospeech.enums.SsmlVoiceGender.FEMALE)

    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16,
        sample_rate_hertz=44100)

    response = client.synthesize_speech(input_text, voice, audio_config)

    # The response's audio_content is binary.
    with open(filename, 'wb') as out:
        out.write(response.audio_content)
        print('Audio content written to file "output.mp3" %s' % language_code)


def list_voices():
    """Lists the available voices."""
    from google.cloud import texttospeech
    from google.cloud.texttospeech import enums
    client = texttospeech.TextToSpeechClient()

    # Performs the list voices request
    voices = client.list_voices()

    for voice in voices.voices:
        # Display the voice's name. Example: tpc-vocoded
        print('Name: {}'.format(voice.name))

        # Display the supported language codes for this voice. Example: "en-US"
        for language_code in voice.language_codes:
            print('Supported language: {}'.format(language_code))

        ssml_gender = enums.SsmlVoiceGender(voice.ssml_gender)

        # Display the SSML Voice Gender
        print('SSML Voice Gender: {}'.format(ssml_gender.name))

        # Display the natural sample rate hertz for this voice. Example: 24000
        print('Natural Sample Rate Hertz: {}\n'.format(
            voice.natural_sample_rate_hertz))


def presigned_post(filename):
    ext = filename.split('.')[1]

    if ext not in ['wav', 'mp3', 'flac', 'm4a']:
        raise Exception("Audio files are acceptable")

    key = 'input/%s' % filename.replace(' ', '_')
    post = s3_client.generate_presigned_post(Bucket='hmapps-audio', Key=key)
    print(key)
    return post


def detect_web_uri(uri):
    """Detects web annotations in the file located in Google Cloud Storage."""
    from google.cloud import vision
    client = vision.ImageAnnotatorClient()
    image = vision.types.Image()
    image.source.image_uri = uri

    response = client.web_detection(image=image)
    annotations = response.web_detection

    # if annotations.best_guess_labels:
    #     for label in annotations.best_guess_labels:
    #         print('\nBest guess label: {}'.format(label.label))

    # if annotations.pages_with_matching_images:
    #     print('\n{} Pages with matching images found:'.format(
    #         len(annotations.pages_with_matching_images)))

    #     for page in annotations.pages_with_matching_images:
    #         print('\n\tPage url   : {}'.format(page.url))

    #         if page.full_matching_images:
    #             print('\t{} Full Matches found: '.format(
    #                 len(page.full_matching_images)))

    #             for image in page.full_matching_images:
    #                 print('\t\tImage url  : {}'.format(image.url))

    #         if page.partial_matching_images:
    #             print('\t{} Partial Matches found: '.format(
    #                 len(page.partial_matching_images)))

    #             for image in page.partial_matching_images:
    #                 print('\t\tImage url  : {}'.format(image.url))

    # if annotations.web_entities:
    #     print('\n{} Web entities found: '.format(
    #         len(annotations.web_entities)))

    #     for entity in annotations.web_entities:
    #         print('\n\tScore      : {}'.format(entity.score))
    #         print(u'\tDescription: {}'.format(entity.description))

    # if annotations.visually_similar_images:
    #     print('\n{} visually similar images found:\n'.format(
    #         len(annotations.visually_similar_images)))

    #     for image in annotations.visually_similar_images:
    #         print('\tImage url    : {}'.format(image.url))

    return annotations
