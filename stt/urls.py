from django.urls import include, path
from rest_framework.routers import DefaultRouter

from stt.views import SttViewSet, FoodViewSet


router = DefaultRouter()

router.register(r'stt', SttViewSet, base_name='stt')
router.register(r'food', FoodViewSet, base_name='food')

sttpatterns = [
    path(r'', include(router.urls)),
]
