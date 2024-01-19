from django.db import models

from core.consts import LENGTH_HEX, LENGTH_TAG_CHARFIELD
from core.validators import hex_color_validator


class Tag(models.Model):
    """Модель тегов рецептов."""

    name = models.CharField(
        'Название тега',
        max_length=LENGTH_TAG_CHARFIELD,
        unique=True,
    )
    color = models.CharField(
        'Цвет тега',
        max_length=LENGTH_HEX,
        unique=True,
        validators=(hex_color_validator,),

    )
    slug = models.SlugField(
        'Слаг тега',
        max_length=LENGTH_TAG_CHARFIELD,
        unique=True,
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'
        ordering = ('-id',)

    def __str__(self):
        return f'{self.name} - {self.slug} - {self.color}'
