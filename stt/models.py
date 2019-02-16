import contextlib
import wave

from django.db import models
from django.utils import timezone

from pydub import AudioSegment
from stt.utils import send_email, transcribe
from zappa.async import task

AudioSegment.converter = './bin/ffmpeg'


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
        if self.audio.name.endswith('mp3'):
            mp3_file = AudioSegment.from_mp3(self.audio.file)
            to_filename = self.audio.name.split('/')[-1].replace('mp3', 'wav')
            mp3_file.export("/tmp/{filename}".format(filename=to_filename), format="wav")
            with open("/tmp/{filename}".format(filename=to_filename), 'br') as fp:
                self.audio.save(to_filename, fp)

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
        email = email if email else 'chharry@naver.com'

        if not self.script:
            raise Exception("Not transcribed")

        send_email(subject='Speech to Text',
                   to_addresses=[email], html=self.script)
