from django.contrib import admin
from stt.models import Stt, Remember, Book, Shelf, BookProgress
from joonggonara.models import Joonggonara


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    pass


@admin.register(Shelf)
class ShelfAdmin(admin.ModelAdmin):
    pass


@admin.register(BookProgress)
class BookProgressAdmin(admin.ModelAdmin):
    pass


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


@admin.register(Remember)
class RememberAdmin(admin.ModelAdmin):
    list_display = ['image_file_tag', 'created_at', 'tag_list', 'user', 'image_file']

    def tag_list(self, obj):
        return u", ".join(o.name for o in obj.tags.all())
