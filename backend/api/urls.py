from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import NewUserViewset, TagViewSet

app_name = 'api'

router = DefaultRouter()
router.register('users', NewUserViewset)
router.register('tags', TagViewSet)

urlpatterns = [
    path('', include(router.urls))

]