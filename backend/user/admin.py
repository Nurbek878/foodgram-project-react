from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import NewUser

class NewUserAdmin(BaseUserAdmin):
    model = NewUser
    fieldsets = (
        (None, {'fields': ('email', 'password', )}),
        (('Персональная информация'), {'fields': ('first_name', 'last_name')}),
        (('Разрешения'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                      'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
          'fields': ('email', 'user_name', 'first_name', 'password', 'is_active', 'is_staff'),
        }),
    )
    list_display = ['email', 'first_name', 'last_name', 'username']
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('username', )

admin.site.register(NewUser, NewUserAdmin)