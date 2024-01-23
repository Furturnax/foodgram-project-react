from django.contrib import admin

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag
)


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
    ordering = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Интерфейс управления рецептами."""

    list_display = (
        'id',
        'author',
        'name',
        'image',
        'text',
        'cooking_time',
        'display_ingredients',
        'display_tags'
    )
    search_fields = ('name',)
    ordering = ('name',)
    empty_value_display = '-пусто-'

    @admin.display(description='Ингредиенты')
    def display_ingredients(self, obj):
        return ', '.join(
            ingredient.name for ingredient in obj.ingredients.all()
        )

    @admin.display(description='Теги')
    def display_tags(self, obj):
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
    search_fields = ('recipe',)
    ordering = ('recipe',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Интерфейс управления избранными рецептами."""

    list_display = (
            'user',
            'recipe',
        )
    search_fields = ('user',)
    ordering = ('user',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Интерфейс управления списком покупок."""

    list_display = (
            'user',
            'recipe',
        )
    search_fields = ('user',)
    ordering = ('user',)
