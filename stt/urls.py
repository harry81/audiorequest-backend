from django.urls import include, path
from rest_framework_nested import routers


from stt.views import (BookViewSet, DogViewSet, KakaoViewSet, PugViewSet,
                       ShelfViewSet, SttViewSet, BookProgressViewSet)

router = routers.SimpleRouter()

router.register(r'stt', SttViewSet, base_name='stt')
router.register(r'kakao', KakaoViewSet, base_name='kakao')
router.register(r'dog', DogViewSet, base_name='dog')
router.register(r'pug', PugViewSet, base_name='pug')
router.register(r'book', BookViewSet, base_name='book')
router.register(r'shelf', ShelfViewSet, base_name='shelf')

shelf_router = routers.NestedSimpleRouter(router, r'shelf', lookup='shelf')
shelf_router.register(r'bookprogress', BookProgressViewSet, base_name='bookprogress')


sttpatterns = [
    path(r'', include(router.urls)),
    path(r'', include(shelf_router.urls)),
]
