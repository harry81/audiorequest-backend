from django.urls import include, path
from rest_framework.routers import DefaultRouter

from stt.views import SttViewSet

router = DefaultRouter()

router.register(r'', SttViewSet, base_name='stt')

sttpatterns = [
    path(r'', include(router.urls)),
]
