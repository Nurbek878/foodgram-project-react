from django.contrib import admin
from recipe.models import Tag, Ingredient

class TagAdmin(admin.ModelAdmin):
    model = Tag
    list_display = ('id','name','slug','color')
    search_fields = ('name',)
    ordering = ('name',)
    list_filter = ('name',)


class IngredientAdmin(admin.ModelAdmin):
    model = Ingredient
    list_display = ('id','name','measurement_unit')
    search_fields = ('name',)
    ordering = ('name',)
    list_filter = ('name',)

admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)