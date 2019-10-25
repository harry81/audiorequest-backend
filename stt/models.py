import contextlib
import logging
import os
import uuid
import wave
from tempfile import NamedTemporaryFile
from urllib.request import urlopen

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.files.storage import default_storage
from django.db import models
from django.utils import timezone
from django.utils.safestring import mark_safe

from storages.backends.gcloud import GoogleCloudStorage
from storages.backends.s3boto3 import S3Boto3Storage
from stt.utils import send_email, transcode, transcribe
from taggit.managers import TaggableManager
from versatileimagefield.fields import VersatileImageField
from zappa.async import task
from stt.utils import detect_web_uri

User = get_user_model()

logger = logging.getLogger(__name__)


@task
def task_process(pk=None, email=None, **kwargs):
    try:
        stt = Stt.objects.get(pk=pk)
    except Stt.DoesNotExist as e:
        logger.error(e)

    if not stt.script:
        stt.transcribe(**kwargs)

    stt.notify(email=email)


class Stt(models.Model):
    audio = models.FileField(upload_to='input', storage=S3Boto3Storage(bucket=settings.AWS_AUDIO_STORAGE_BUCKET_NAME))
    audio_type = models.CharField(max_length=8, null=True, blank=True)
    audio_channels = models.IntegerField(default=1)
    lang_code = models.CharField(max_length=8, default='ko-KR')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    script = models.TextField(blank=True, null=True)
    duration = models.FloatField(default=0)
    created_at = models.DateTimeField(default=timezone.now, blank=True, null=True)

    def save(self, *args, **kwargs):
        super(Stt, self).save(*args, **kwargs)

    def __str__(self):
        return '%s' % (self.audio)

    @property
    def audio_name(self):
        return "%s.%s" % (self.audio.name.split('.')[0], settings.AUDIO_EXT[0])

    @property
    def hearable_audio_url(self):
        ext = self.audio.name.split('.')[1]

        if ext in ['amr']:
            return default_storage.url(self.audio.name.replace(ext, settings.AUDIO_EXT[0]))

        return self.audio.url

    def set_audio_meta(self):
        with contextlib.closing(wave.open(default_storage.open(self.audio_name, 'r'))) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            self.duration = frames / float(rate)
            self.audio_channels = f.getnchannels()

        self.save()

    # step1 - transfer
    # step2 - move
    # step3 - transcribe
    def transcribe(self, **kwargs):
        # step1
        from google.cloud import storage
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(settings.GS_BUCKET_NAME)

        is_transfered = False
        if not self.audio.name.split(".")[1] in settings.AUDIO_EXT:
            transcribable_filename = "%s.%s" % (self.audio.name.split(".")[0], settings.AUDIO_EXT[0])
        else:
            transcribable_filename = self.audio.name

        for ext in settings.AUDIO_EXT:
            if bucket.get_blob(transcribable_filename):
                is_transfered = True
                break

        # step2
        ext = self.audio.name.split('.')[1]

        if ext not in settings.AUDIO_EXT and not is_transfered and not default_storage.exists(transcribable_filename):
            try:
                transcode(self.audio.name)
            except Exception as e:
                logging.error(e)

        blob = bucket.blob(transcribable_filename)

        if not blob.exists():
            blob.upload_from_file(self.audio.storage.open(transcribable_filename))

        # step3
        response = transcribe(filename=transcribable_filename, **kwargs)

        self.script = "\n".join([result.alternatives[0].transcript for result in response.results])
        self.save()

    def notify(self, email=None):
        email = email if email else settings.DEFAULT_EMAIL_ADDRESS

        if not self.script:
            raise Exception("Not transcribed")

        addresses = list(set([email]))
        send_email(subject='Speech to Text', to_addresses=addresses, html=self.script)


class Remember(models.Model):
    image_file = VersatileImageField('Image', upload_to='remember/',
                                     storage=GoogleCloudStorage(bucket="pointer-bucket"))
    image_url = models.URLField()
    created_at = models.DateTimeField(default=timezone.now, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    tags = TaggableManager()

    def save(self, *args, **kwargs):
        super(Remember, self).save(*args, **kwargs)
        if self.image_url and not self.image_file:
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(urlopen(self.image_url).read())
            img_temp.flush()
            self.image_file.save(os.path.basename(self.image_url), File(img_temp))

    def get_tags(self):
        uri = "gs://%s/%s" % ('pointer-bucket', self.image_file.name)
        annotations = detect_web_uri(uri)
        self.tags.add(*[ele.description for ele in annotations.web_entities[:5]])

        return self.tags.slugs()

    def __str__(self):
        return '%s' % (self.image_file.name)

    def image_file_tag(self, length=50):
        if self.image_url:
            return mark_safe('<img src="%s" width="%d" height="%d" />' % (self.image_url, length, length))
        else:
            return None
