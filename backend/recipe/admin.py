from django.contrib import admin
from recipe.models import IngredientRecipe, Tag, Ingredient, Recipe, TagRecipe

class TagAdmin(admin.ModelAdmin):
    model = Tag
    list_display = ('id','name','slug','color')
    search_fields = ('name',)
    ordering = ('name',)


class IngredientAdmin(admin.ModelAdmin):
    model = Ingredient
    list_display = ('id','name','measurement_unit')
    search_fields = ('name',)
    ordering = ('name',)
    list_filter = ('name',)


class IngredientRecipeInLine(admin.TabularInline):
    model = IngredientRecipe


class TagRecipeInLine(admin.TabularInline):
    model = TagRecipe


class RecipeAdmin(admin.ModelAdmin):
    model = Recipe
    list_filter = ('name', 'author',)
    list_display = ('id', 'name', 'text', 'cooking_time', 'author')
    search_fields = ('name',)
    ordering = ('name',)
    inlines = [IngredientRecipeInLine, TagRecipeInLine]

admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)