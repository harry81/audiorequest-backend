from django.db import models
from django.utils import timezone


class Joonggonara(models.Model):
    id = models.CharField(max_length=32, primary_key=True)
    title = models.CharField(max_length=128, null=True, blank=True)
    username = models.CharField(max_length=64, null=True, blank=True)
    category = models.CharField(max_length=64, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, blank=True, null=True)
