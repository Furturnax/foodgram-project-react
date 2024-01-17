from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Follow, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Интерфейс управления пользователями."""

    list_display = (
        'id', 'username', 'email', 'first_name', 'last_name'
    )
    search_fields = ('username', 'email')
    ordering = ('-id',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Настройка раздела Подписки."""

    list_display = ('following', 'user')
    search_fields = ('following',)
