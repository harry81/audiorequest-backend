from django.contrib import admin
from stt.models import Stt


@admin.register(Stt)
class SttAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'pk', 'uuid', 'duration', 'audio_channels', 'created_at']
    search_fields = ['audio']
    readonly_fields = ['created_at']
