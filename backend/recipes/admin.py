from django.contrib import admin

from recipes.models import Ingredient, Tag


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
    """Интерфейс управления тегами."""

    list_display = (
            'id',
            'name',
            'measurement_unit'
        )
    search_fields = ('name',)
    ordering = ('name',)
