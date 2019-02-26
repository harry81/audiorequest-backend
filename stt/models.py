import contextlib
import logging
import wave

from django.conf import settings
from django.core.files.storage import default_storage
from django.db import models
from django.utils import timezone

from pydub import AudioSegment
from stt.utils import convert_audio, send_email, transcribe
from zappa.async import task

AudioSegment.converter = settings.AUDIO_CONVERTER_PATH


@task
def task_process(pk=None, email=None, **kwargs):
    stt = Stt.objects.get(pk=pk)
    stt.transcribe(**kwargs)
    stt.notify(email=email)


class Stt(models.Model):
    audio = models.FileField(upload_to='audio')
    audio_type = models.CharField(max_length=8, null=True, blank=True)
    audio_channels = models.IntegerField(default=1)
    lang_code = models.CharField(max_length=8, default='ko-KR')
    script = models.TextField(blank=True, null=True)
    duration = models.FloatField(default=0)
    created_at = models.DateTimeField(default=timezone.now, blank=True, null=True)

    def save(self, *args, **kwargs):
        ext = self.audio.name[-3:]

        if ext != settings.AUDIO_EXT and not default_storage.exists(self.audio_name):
            try:
                convert_audio(self.audio)
            except Exception as e:
                logging.error(e)

        super(Stt, self).save(*args, **kwargs)

    def __str__(self):
        return '%s' % (self.audio)

    @property
    def audio_name(self):
        return "%s%s" % (self.audio.name[:-3], settings.AUDIO_EXT)

    def set_audio_meta(self):
        with contextlib.closing(wave.open(default_storage.open(self.audio_name, 'r'))) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            self.duration = frames / float(rate)
            self.audio_channels = f.getnchannels()

        self.save()

    def transcribe(self, **kwargs):
        response = transcribe(filename=self.audio_name, **kwargs)

        self.script = "\n".join([result.alternatives[0].transcript for result in response.results])
        self.save()

    def notify(self, email=None):
        email = email if email else settings.DEFAULT_EMAIL_ADDRESS

        if not self.script:
            raise Exception("Not transcribed")

        addresses = list(set([email]))
        send_email(subject='Speech to Text', to_addresses=addresses, html=self.script)
