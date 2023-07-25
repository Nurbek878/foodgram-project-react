from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import NewUserViewset, TagViewSet, IngredientViewSet

app_name = 'api'

router = DefaultRouter()
router.register('users', NewUserViewset)
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)

urlpatterns = [
    path('', include(router.urls))

]