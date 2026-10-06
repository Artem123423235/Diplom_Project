from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ('username', 'email', 'full_name', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'full_name')
    ordering = ('-date_joined',)

    # Добавляем role и full_name к стандартным fieldsets
    fieldsets = DjangoUserAdmin.fieldsets + (
        ('Роль и профиль', {'fields': ('role', 'full_name')}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ('Роль и профиль', {'fields': ('email', 'role', 'full_name')}),
    )
    readonly_fields = ('date_joined', 'last_login')
