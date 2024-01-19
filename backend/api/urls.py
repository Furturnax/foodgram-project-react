from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from api.views import TagWievSet, UserViewSet

app_name = 'api'

router = DefaultRouter()

router.register('users', UserViewSet, 'users')
router.register('tags', TagWievSet, 'tags')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
