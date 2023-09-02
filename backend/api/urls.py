from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (FavoriteRecipeView, IngredientViewSet, NewUserViewset,
                    RecipeViewSet, ShoppingRecipeView, SubscribeUserView,
                    SubscriptionUserView, TagViewSet, download_list)

app_name = 'api'

router = DefaultRouter()
router.register('users', NewUserViewset)
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)

urlpatterns = [
    path('recipes/<int:pk>/favorite/',
         FavoriteRecipeView.as_view()),
    path('recipes/<int:pk>/shopping_cart/',
         ShoppingRecipeView.as_view()),
    path('recipes/download_shopping_cart/',
         download_list, name='download_list'),
    path('users/<int:pk>/subscribe/',
         SubscribeUserView.as_view()),
    path(
        'users/subscriptions/',
        SubscriptionUserView.as_view(),
        name='subscriptions'
    ),
    path('', include(router.urls))
]
