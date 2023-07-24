from django.contrib import admin
from recipe.models import Tag

class TagAdmin(admin.ModelAdmin):
    model = Tag
    list_display = ('id','name','slug','color')
    search_fields = ('name',)
    ordering = ('name',)
    list_filter = ('name',)

admin.site.register(Tag, TagAdmin)
