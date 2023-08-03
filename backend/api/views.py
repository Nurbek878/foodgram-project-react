from djoser.views import UserViewSet
from rest_framework import viewsets, pagination, permissions, mixins
from api.serializers import (NewUserSerializer, TagSerializer,
                             IngredientSetSerializer, RecipeListRetrieveSerializer,
                             RecipeCreateUpdateSerializer)
from user.models import NewUser
from recipe.models import Tag, Ingredient, Recipe

class NewUserViewset(UserViewSet):
    queryset = NewUser.objects.all()
    pagination_class = pagination.PageNumberPagination
    serializer_class = NewUserSerializer


class IngridientTagListRetrieveViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
    pagination_class = None
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,]


class TagViewSet(IngridientTagListRetrieveViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(IngridientTagListRetrieveViewSet):
    serializer_class = IngredientSetSerializer
    queryset = Ingredient.objects.all()


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,]
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.action in ('list','retrieve'):
            return RecipeListRetrieveSerializer
        return RecipeCreateUpdateSerializer