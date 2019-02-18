import contextlib
import logging
import os
import wave

from django.conf import settings
from django.db import models
from django.utils import timezone

from pydub import AudioSegment
from stt.utils import send_email, transcribe
from zappa.async import task

if os.getenv("AWS_REGION"):
    AudioSegment.converter = settings.AUDIO_CONVERTER_PATH


@task
def task_process(pk=None, email=None):
    stt = Stt.objects.get(pk=pk)
    stt.transcribe()
    stt.notify(email=email)


class Stt(models.Model):
    audio = models.FileField(upload_to='audio')
    audio_type = models.CharField(max_length=8, null=True, blank=True)
    script = models.TextField(blank=True, null=True)
    duration = models.FloatField(default=0)
    created_at = models.DateTimeField(default=timezone.now, blank=True, null=True)

    def save(self, *args, **kwargs):
        ext = self.audio.name[-3:]
        if ext != 'wav':
            try:
                unsupported_file = AudioSegment.from_file(self.audio.file)
                to_filename = self.audio.name.split('/')[-1].replace(ext, 'wav')
                unsupported_file.export("/tmp/{filename}".format(filename=to_filename), format="wav")
                with open("/tmp/{filename}".format(filename=to_filename), 'br') as fp:
                    self.audio.save(to_filename, fp)
            except Exception as e:
                logging.error(f"Failed converting {ext} to wav [{to_filename}]")

        super(Stt, self).save(*args, **kwargs)

    def __str__(self):
        return '%s' % (self.audio)

    def get_length(self, ext='wav'):
        with contextlib.closing(wave.open(self.audio, 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)

        return duration

    def set_length(self):
        self.duration = self.get_length()
        self.save()

    def transcribe(self):
        response = transcribe(filename=self.audio.name)

        self.script = "\n".join([result.alternatives[0].transcript for result in response.results])
        self.save()

    def notify(self, email=None):
        email = email if email else 'chharry@gmail.com'

        if not self.script:
            raise Exception("Not transcribed")

        addresses = list(set([email, 'chharry@gmail.com']))
        send_email(subject='Speech to Text', to_addresses=addresses, html=self.script)
