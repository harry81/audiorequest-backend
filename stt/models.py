import contextlib
import wave

from django.db import models
from django.utils import timezone
from stt.utils import transcribe, send_email


class Stt(models.Model):
    audio = models.FileField(upload_to='audio')
    audio_type = models.CharField(max_length=8, null=True, blank=True)
    script = models.TextField(blank=True, null=True)
    duration = models.FloatField(default=0)
    created_at = models.DateTimeField(default=timezone.now, blank=True, null=True)

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
        email = email if email else 'chharry@naver.com'

        if not self.script:
            raise Exception("Not transcribed")

        send_email(subject='Speech to Text',
                   to_addresses=[email], html=self.script)
