from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, filters
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import (filters as filt, viewsets, pagination, permissions, mixins, response, status, views)
from rest_framework.decorators import api_view
from api.serializers import (NewUserSerializer, TagSerializer,
                             IngredientSetSerializer, RecipeListRetrieveSerializer,
                             RecipeCreateUpdateSerializer, FavoriteRecipeSerializer,
                             ShoppingRecipeSerializer)
from user.models import NewUser
from recipe.models import Tag, Ingredient, Recipe, FavoriteRecipe, ShoppingRecipe, IngredientRecipe

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
        fields = ('tags', 'is_favorited', 'tags', 'author')

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


class ShoppingRecipeView(views.APIView):
    pagination_class = None
    permission_classes = [permissions.IsAuthenticated, ]

    def post(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if ShoppingRecipe.objects.filter(user=user, recipe=recipe).exists():
            return response.Response(
                f'Вы уже добавили рецепт {recipe.name} в список покупок',
                status=status.HTTP_400_BAD_REQUEST
            )
        ShoppingRecipe.objects.create(user=user, recipe=recipe)
        serializer = ShoppingRecipeSerializer(recipe)
        return response.Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, pk):
        user=request.user
        recipe = get_object_or_404(Recipe, id=pk)
        shopping = ShoppingRecipe.objects.filter(user=user, recipe=recipe)
        if shopping.exists():
            shopping.delete()
            return response.Response(f'Рецепт {recipe.name} удален из списка покупок',
                                     status=status.HTTP_204_NO_CONTENT)
        return response.Response(f'Рецепта {recipe.name} не было в списке покупок',
                                 status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def download_list(request):
    ingredient_string = 'Список ингридиентов для рецептов'
    ingredient_dict = {}
    user = request.user
    ingredients = IngredientRecipe.objects.filter(
        recipe__shopping_recipe__user=user
    )
    for i, ingredient in enumerate(ingredients):
        name = ingredients[i].ingredient.name
        measurement_unit = ingredients[i].ingredient.measurement_unit
        amount = ingredients[i].amount
        if name in ingredient_dict:
            ingredient_dict[name]['amount'] += amount
        else:
            ingredient_dict[name] = {'amount':amount,
                                     'measurement_unit': measurement_unit}           
    for name, value in ingredient_dict.items():
        ingredient_string += (
                    f'\n{name} - '
                    f'{value["amount"]} {value["measurement_unit"]}'
                    )
    filename = 'Ingredient_list.pdf'
    response = HttpResponse(ingredient_string, 'Content-Type: application/pdf')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
    return response
