from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import filters as filt
from rest_framework import (generics, mixins, permissions, response, status,
                            views, viewsets)
from rest_framework.decorators import api_view

from api.filters import CustomRecipeFilter
from api.serializers import (FavoriteRecipeSerializer, IngredientSetSerializer,
                             NewUserSerializer, RecipeCreateUpdateSerializer,
                             RecipeListRetrieveSerializer,
                             ShoppingRecipeSerializer,
                             SubscribeReturnSerializer,
                             SubscribeUserSerializer, TagSerializer)
from recipe.models import (FavoriteRecipe, Ingredient, IngredientRecipe,
                           Recipe, ShoppingRecipe, Tag)
from user.models import NewUser, Subscription


class NewUserViewset(UserViewSet):
    queryset = NewUser.objects.all()
    serializer_class = NewUserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]


class IngridientTagListRetrieveViewSet(mixins.ListModelMixin,
                                       mixins.RetrieveModelMixin,
                                       viewsets.GenericViewSet):
    pagination_class = None
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]


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


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CustomRecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeListRetrieveSerializer
        return RecipeCreateUpdateSerializer


class FavoriteRecipeView(views.APIView):
    pagination_class = None
    permission_classes = [permissions.IsAuthenticated, ]

    def post(self, request, pk):
        user = request.user
        serializer = FavoriteRecipeSerializer(
                data={'user': user.id, 'recipe': pk},
                context={'request': self.request}
            )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data,
                                 status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        favorite = FavoriteRecipe.objects.filter(user=user, recipe=recipe)
        if favorite.exists():
            favorite.delete()
            return response.Response(
                f'Рецепт {recipe.name} удален из избранного',
                status=status.HTTP_204_NO_CONTENT)
        return response.Response(
            f'Рецепта {recipe.name} не было в избранном',
            status=status.HTTP_400_BAD_REQUEST)


class ShoppingRecipeView(views.APIView):
    pagination_class = None
    permission_classes = [permissions.IsAuthenticated, ]

    def post(self, request, pk):
        user = request.user
        serializer = ShoppingRecipeSerializer(
                data={'user': user.id, 'recipe': pk},
                context={'request': self.request}
            )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data,
                                 status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        shopping = ShoppingRecipe.objects.filter(user=user, recipe=recipe)
        if shopping.exists():
            shopping.delete()
            return response.Response(
                f'Рецепт {recipe.name} удален из списка покупок',
                status=status.HTTP_204_NO_CONTENT)
        return response.Response(
            f'Рецепта {recipe.name} не было в списке покупок',
            status=status.HTTP_400_BAD_REQUEST)


class SubscribeUserView(views.APIView):
    pagination_class = None
    permission_classes = [permissions.IsAuthenticated, ]

    def post(self, request, pk):
        subscriber = request.user
        serializer = SubscribeUserSerializer(
            data={'subscriber': subscriber.id, 'subscribe': pk},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return response.Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, pk):
        subscriber = request.user
        subscribe = get_object_or_404(NewUser, id=pk)
        subscribing = Subscription.objects.filter(subscriber=subscriber,
                                                  subscribe=subscribe)
        if subscribing.exists():
            subscribing.delete()
            return response.Response(
                f'Пользователь {subscriber} отписался от {subscribe}',
                status=status.HTTP_204_NO_CONTENT)
        return response.Response(
            f'Пользователь {subscriber} не подписан на {subscribe}',
            status=status.HTTP_400_BAD_REQUEST)


class SubscriptionUserView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = SubscribeReturnSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    def get_queryset(self):
        user = self.request.user
        return NewUser.objects.filter(subscribed_by__subscriber=user)


@api_view(['GET'])
def download_list(request):
    ingredient_note = 'Список ингридиентов для рецептов'
    unique_names = {}
    user = request.user
    ingredients = IngredientRecipe.objects.values(
        'ingredient__name', 'ingredient__measurement_unit',
        ).annotate(amount_ingredients=Count('amount')).filter(
        recipe__shopping_recipe__user=user
        )
    for i, ingredient in enumerate(ingredients):
        name = ingredient["ingredient__name"]
        measurement_unit = ingredient["ingredient__measurement_unit"]
        amount = ingredient["amount_ingredients"]
        if name in unique_names:
            unique_names[name]['amount'] += amount
        else:
            unique_names[name] = {'amount': amount,
                                  'measurement_unit': measurement_unit}

    for name, value in unique_names.items():
        ingredient_note += (
            f'\n{name} - '
            f'{value["amount"]} {value["measurement_unit"]}'
        )
    filename = 'Ingredient_list.pdf'
    response = HttpResponse(ingredient_note, 'Content-Type: application/pdf')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(
        filename)
    return response
