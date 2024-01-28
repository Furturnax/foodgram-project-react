from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag
)

admin.site.empty_value_display = 'Не задано'

admin.site.unregister(Group)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Интерфейс управления тегами."""

    list_display = (
        'id',
        'name',
        'color',
        'slug'
    )
    search_fields = (
        'name',
        'slug'
    )
    list_filter = (
        'name',
        'slug'
    )
    list_display_links = ('name',)
    ordering = ('name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Интерфейс управления ингредиентами."""

    list_display = (
        'id',
        'name',
        'measurement_unit'
    )
    search_fields = ('name',)
    list_filter = ('name',)
    list_display_links = ('name',)
    ordering = ('name',)


class IngredientInline(admin.TabularInline):
    """Интерфейс управления ингредиентами в рецепте."""
    model = RecipeIngredient
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Интерфейс управления рецептами."""

    list_display = (
        'id',
        'author',
        'name',
        'image_tag',
        'text',
        'cooking_time',
        'display_ingredients',
        'display_tags',
        'in_favourite_count'
    )
    search_fields = (
        'name',
        'author__username',
        'tags__name'
    )
    list_filter = (
        'name',
        'author__username',
        'tags__name'
    )
    list_display_links = ('name',)
    ordering = ('-pub_date',)
    inlines = (IngredientInline,)
    readonly_fields = (
        'image_tag',
        'in_favourite_count'
    )

    def image_tag(self, obj):
        """Добавляет изображение в разделе рецепты."""
        if obj.image:
            return mark_safe(
                f'<img src={obj.image.url} width="80" height="60">'
            )
        return 'Нет изображения'
    image_tag.short_description = 'Изображение'

    def in_favourite_count(self, obj):
        """Возвращает количество рецептов в избранном."""
        return Favorite.objects.filter(recipe=obj).count()
    in_favourite_count.short_description = 'В избранном'

    @admin.display(description='Ингредиенты')
    def display_ingredients(self, obj):
        """Добавляет ингредиенты в разделе рецепты."""
        return ', '.join(
            ingredient.name for ingredient in obj.ingredients.all()
        )

    @admin.display(description='Теги')
    def display_tags(self, obj):
        """Добавляет теги в разделе рецепты."""
        return ', '.join(
            tag.name for tag in obj.tags.all()
        )


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """Интерфейс управления игредиентами в рецепте."""

    list_display = (
        'recipe',
        'ingredient',
        'amount'
    )
    search_fields = (
        'recipe__name',
        'ingredient__name'
    )
    list_filter = ('recipe__name',)
    list_display_links = ('recipe',)
    ordering = ('recipe',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Интерфейс управления избранными рецептами."""

    list_display = (
        'user',
        'recipe'
    )
    search_fields = (
        'user__username',
        'recipe__name'
    )
    list_filter = (
        'user__username',
        'recipe__name'
    )
    list_display_links = ('user',)
    ordering = ('user',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Интерфейс управления списком покупок."""

    list_display = (
        'user',
        'recipe'
    )
    search_fields = ('user__username',)
    list_filter = (
        'user__username',
        'recipe__name'
    )
    list_display_links = ('user',)
    ordering = ('user',)
