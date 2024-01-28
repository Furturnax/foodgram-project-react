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
        'email',
        'first_name',
        'last_name',
    )
    list_filter = (
        'first_name',
        'email'
    )
    list_display_links = ('username',)
    ordering = ('-id',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Интерфейс управления подписками."""

    list_display = (
        'following',
        'user'
    )
    search_fields = ('following__username',)
    list_filter = (
        'following',
        'user'
    )
    list_display_links = (
        'following',
        'user'
    )
    ordering = ('following',)
