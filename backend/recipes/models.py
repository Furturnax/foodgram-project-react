from django.db import models

from core.consts import LENGTH_HEX, LENGTH_TAG_AND_INGREDIENT_CHARFIELD
from core.validators import hex_color_validator, slug_validator


class Tag(models.Model):
    """Модель тегов рецептов."""

    name = models.CharField(
        'Название тега',
        max_length=LENGTH_TAG_AND_INGREDIENT_CHARFIELD,
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
        max_length=LENGTH_TAG_AND_INGREDIENT_CHARFIELD,
        unique=True,
        validators=(slug_validator,),
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'
        ordering = ('-id',)

    def __str__(self):
        return f'{self.name} - {self.slug} - {self.color}'


class Ingredient(models.Model):
    """Модель ингредиентов рецептов."""

    name = models.CharField(
        'Название ингредиента',
        max_length=LENGTH_TAG_AND_INGREDIENT_CHARFIELD
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=LENGTH_TAG_AND_INGREDIENT_CHARFIELD
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} - {self.measurement_unit}'
