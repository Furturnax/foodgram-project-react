from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Follow, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Интерфейс управления пользователями."""

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Личная информация', {'fields': ('first_name', 'last_name')})
    )
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'is_superuser',
        'is_active',
        'recipe_count',
        'following_count',
    )
    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name',
    )
    list_filter = (
        'first_name',
        'email',
    )
    list_display_links = ('username',)
    ordering = ('last_name', 'first_name')
    readonly_fields = (
        'recipe_count',
        'following_count',
    )

    @admin.display(description='Рецепты')
    def recipe_count(self, obj):
        """Возвращает количество рецептов пользователя."""
        return obj.recipes.count()

    @admin.display(description='Подписки')
    def following_count(self, obj):
        """Возвращает количество подписок пользователя."""
        return obj.following.count()


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Интерфейс управления подписками."""

    list_display = (
        'following',
        'user',
    )
    search_fields = ('following__username',)
    list_filter = (
        'following',
        'user',
    )
    list_display_links = (
        'following',
        'user',
    )
    ordering = ('following',)
