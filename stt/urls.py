from django.urls import include, path
from rest_framework.routers import DefaultRouter

from stt.views import SttViewSet, KakaoViewSet, DogViewSet, PugViewSet


router = DefaultRouter()

router.register(r'stt', SttViewSet, base_name='stt')
router.register(r'kakao', KakaoViewSet, base_name='kakao')
router.register(r'dog', DogViewSet, base_name='dog')
router.register(r'pug', PugViewSet, base_name='pug')

sttpatterns = [
    path(r'', include(router.urls)),
]
