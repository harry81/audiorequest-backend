from django.utils import timezone
from django.db import models


class Stt(models.Model):
    audio = models.FileField(upload_to='audio')
    audio_type = models.CharField(max_length=8, null=True, blank=True)
    script = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now, blank=True, null=True)

    def __str__(self):
        return '%s' % (self.audio)
