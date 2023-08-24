from django_filters.rest_framework import DjangoFilterBackend, FilterSet, filters
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import (filters as filt, viewsets, pagination, permissions, mixins, response, status, views)
from api.serializers import (NewUserSerializer, TagSerializer,
                             IngredientSetSerializer, RecipeListRetrieveSerializer,
                             RecipeCreateUpdateSerializer, FavoriteRecipeSerializer,)
from user.models import NewUser
from recipe.models import Tag, Ingredient, Recipe, FavoriteRecipe

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


class CustomIngredientFilter(filt.SearchFilter):
    search_param = 'name'


class IngredientViewSet(IngridientTagListRetrieveViewSet):
    serializer_class = IngredientSetSerializer
    queryset = Ingredient.objects.all()
    filter_backends = (CustomIngredientFilter,)
    search_fields = ('^name',)


class CustomRecipeFilter(FilterSet):
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    tags = filters.ModelMultipleChoiceFilter(field_name='tags__slug',
                                             to_field_name='slug',
                                             queryset=Tag.objects.all())
        
    class Meta:
        model = Recipe
        fields = ('tags', 'is_favorited', 'tags')

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            return queryset.filter(favorite_recipe__user=user)
        return queryset
        

class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,]
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CustomRecipeFilter

    def get_serializer_class(self):
        if self.action in ('list','retrieve'):
            return RecipeListRetrieveSerializer
        return RecipeCreateUpdateSerializer
    

class FavoriteRecipeView(views.APIView):

    pagination_class = None
    permission_classes = [permissions.IsAuthenticated, ]
    
    def post(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if FavoriteRecipe.objects.filter(user=user, recipe=recipe).exists():
            return response.Response(
                f'Вы уже добавили рецепт {recipe.name} в избранное',
                status=status.HTTP_400_BAD_REQUEST
            )
        FavoriteRecipe.objects.create(user=user, recipe=recipe)
        serializer = FavoriteRecipeSerializer(recipe)
        return response.Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, pk):
        user=request.user
        recipe = get_object_or_404(Recipe, id=pk)
        favorite = FavoriteRecipe.objects.filter(user=user, recipe=recipe)
        if favorite.exists():
            favorite.delete()
            return response.Response(f'Рецепт {recipe.name} удален из избранного',
                                     status=status.HTTP_204_NO_CONTENT)
        return response.Response(f'Рецепта {recipe.name} не было в избранном', 
                                 status=status.HTTP_400_BAD_REQUEST)
