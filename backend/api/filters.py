from django_filters.rest_framework import FilterSet, filters

from recipe.models import Recipe, Tag


class CustomRecipeFilter(FilterSet):
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')
    tags = filters.ModelMultipleChoiceFilter(field_name='tags__slug',
                                             to_field_name='slug',
                                             queryset=Tag.objects.all())

    class Meta:
        model = Recipe
        fields = ('tags', 'is_favorited', 'tags',
                  'author', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            return queryset.filter(favorite_recipe__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            return queryset.filter(shopping_recipe__user=user)
        return queryset
