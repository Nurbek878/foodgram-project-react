from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import NewUserViewset, TagViewSet, IngredientViewSet, RecipeViewSet, FavoriteRecipeView

app_name = 'api'

router = DefaultRouter()
router.register('users', NewUserViewset)
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)

urlpatterns = [
    path('recipes/<int:pk>/favorite/',
         FavoriteRecipeView.as_view()),
    path('', include(router.urls))

]