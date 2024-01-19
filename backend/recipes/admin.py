from django.contrib import admin

from recipes.models import Tag


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
    ordering = ('-id',)
