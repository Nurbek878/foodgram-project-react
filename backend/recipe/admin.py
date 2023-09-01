from django.contrib import admin
from recipe.models import (IngredientRecipe, Tag, Ingredient,
                           Recipe, TagRecipe, FavoriteRecipe,
                           ShoppingRecipe)


class TagAdmin(admin.ModelAdmin):
    model = Tag
    list_display = ('id', 'name', 'slug', 'color')
    search_fields = ('name',)
    ordering = ('name',)


class IngredientAdmin(admin.ModelAdmin):
    model = Ingredient
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    ordering = ('name',)
    list_filter = ('name',)


class IngredientRecipeInLine(admin.TabularInline):
    model = IngredientRecipe


class TagRecipeInLine(admin.TabularInline):
    model = TagRecipe


class FavoriteRecipe(admin.TabularInline):
    model = FavoriteRecipe


class ShoppingRecipe(admin.TabularInline):
    model = ShoppingRecipe


class RecipeAdmin(admin.ModelAdmin):
    model = Recipe
    list_filter = ('name', 'author', 'tags')
    list_display = ('id', 'name', 'text', 'cooking_time', 'author',
                    'is_favorited')
    search_fields = ('name',)
    ordering = ('name',)
    inlines = [IngredientRecipeInLine, TagRecipeInLine,
               FavoriteRecipe, ShoppingRecipe]

    def is_favorited(self, obj):
        return obj.favorite_recipe.count()


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
