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
    search_fields = ('name', 'color')
    list_filter = ('name', 'color', 'slug')
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
    search_fields = ('name', 'measurement_unit')
    list_filter = ('name', 'measurement_unit')
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
        'display_tags'
    )
    search_fields = ('name', 'author', 'tags', 'cooking_time')
    list_filter = ('name', 'author', 'tags', 'cooking_time')
    list_display_links = ('name',)
    ordering = ('name',)
    inlines = (IngredientInline,)
    readonly_fields = ('image_tag',)

    def image_tag(self, obj):
        """Добавляет изображение в разделе рецепты."""
        if obj.image:
            return mark_safe(
                f'<img src={obj.image.url} width="80" height="60">'
            )
        return 'Нет изображения'
    image_tag.short_description = 'Изображение'

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
        'amount',
    )
    search_fields = ('recipe', 'ingredient')
    list_filter = ('recipe', 'ingredient')
    list_display_links = ('recipe',)
    ordering = ('recipe',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Интерфейс управления избранными рецептами."""

    list_display = (
        'user',
        'recipe',
    )
    search_fields = ('user',)
    list_filter = ('user', 'recipe')
    list_display_links = ('user',)
    ordering = ('user',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Интерфейс управления списком покупок."""

    list_display = (
        'user',
        'recipe',
    )
    search_fields = ('user',)
    list_filter = ('user', 'recipe')
    list_display_links = ('user',)
    ordering = ('user',)
