from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import NewUser, Subscription


class NewUserAdmin(BaseUserAdmin):
    model = NewUser
    fieldsets = (
        (('Данные для входа'), {'fields': ('email', 'password', )}),
        (('Персональная информация'), {'fields': ('first_name', 'last_name')}),
        (('Разрешения'), {'fields': ('is_active',
                                     'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (('Данные для регистрации пользователя'), {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'username',
                       'email', 'password1', 'password2'),
        }),
    )
    list_display = ['id', 'email', 'first_name', 'last_name', 'username']
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('id', )
    list_filter = ('username', 'email',)


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'subscriber', 'subscribe']
    search_fields = ('subscriber', 'subscribe')
    list_filter = ('subscriber', 'subscribe')


admin.site.register(NewUser, NewUserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
