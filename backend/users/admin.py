from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Follow, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Интерфейс управления пользователями."""

    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'is_superuser',
        'is_active'
    )
    search_fields = (
        'username',
        'first_name',
        'is_staff',
        'is_superuser',
        'is_active'
    )
    list_filter = ('username', 'first_name')
    list_display_links = ('username',)
    ordering = ('-id',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Интерфейс управления подписками."""

    list_display = ('following', 'user')
    search_fields = ('following',)
    list_filter = ('following', 'user')
    list_display_links = ('following',)
    ordering = ('following',)
