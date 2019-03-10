from django.contrib import admin
from stt.models import Stt
from joonggonara.models import Joonggonara


@admin.register(Stt)
class SttAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'pk', 'lang_code', 'uuid', 'duration', 'audio_channels', 'created_at']
    search_fields = ['audio']
    readonly_fields = ['created_at']


@admin.register(Joonggonara)
class JoonggonaraAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'title', 'category', 'created_at']
    search_fields = ['title', 'category']
    readonly_fields = ['created_at']
