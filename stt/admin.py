from django.contrib import admin
from stt.models import Stt


@admin.register(Stt)
class SttAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'pk', 'duration', 'audio_channels', 'created_at']
    readonly_fields = ['created_at']
