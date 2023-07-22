from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import NewUserViewset

app_name = 'api'

router = DefaultRouter()
router.register('users', NewUserViewset)

urlpatterns = [
    path('', include(router.urls))
]