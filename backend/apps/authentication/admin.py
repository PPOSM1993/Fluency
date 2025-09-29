from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ['email']
    list_display = [
        'email', 'username', 'first_name', 'last_name',
        'is_active', 'is_staff', 'is_superuser'
    ]
    list_filter = ['is_active', 'is_staff', 'is_superuser']
    search_fields = ['email', 'username', 'rut', 'first_name', 'last_name']
    readonly_fields = ['date_joined']

    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        (_('Información personal'), {
            'fields': ('first_name', 'last_name', 'rut', 'phone', 'birth_date')
        }),
        (_('Estado'), {'fields': ('is_active', 'accepted_terms')}),
        (_('Permisos y roles'), {
            'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Fechas importantes'), {'fields': ('date_joined',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': [
                'email', 'username', 'first_name', 'last_name',
                'password1', 'password2', 'is_active'
            ],
        }),
    )