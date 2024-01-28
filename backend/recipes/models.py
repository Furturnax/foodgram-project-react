from django.core.validators import MinValueValidator
from django.db import models

from core.consts import (
    LENGTH_HEX,
    LENGTH_TAG_AND_INGREDIENT_CHARFIELD,
    MAX_TEXT_RECIPES,
    MIN_VALUE_VALIDATOR
)
from core.validators import hex_color_validator, slug_validator
from users.models import User


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
        ordering = ('id',)

    def __str__(self):
        return f'{self.name} - {self.slug} - {self.color}'


class Ingredient(models.Model):
    """Модель ингредиентов рецептов."""

    name = models.CharField(
        'Название ингредиента',
        max_length=LENGTH_TAG_AND_INGREDIENT_CHARFIELD,
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=LENGTH_TAG_AND_INGREDIENT_CHARFIELD,
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} - {self.measurement_unit}'


class Recipe(models.Model):
    """Модель рецептов."""

    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        'Название рецепта',
        max_length=LENGTH_TAG_AND_INGREDIENT_CHARFIELD,
    )
    image = models.ImageField(
        'Картинка рецепта',
        upload_to='recipes/images/',
    )
    text = models.TextField(
        'Описание рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        through='RecipeIngredient',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления в минутах',
        validators=(MinValueValidator(
            MIN_VALUE_VALIDATOR,
            message='Не менее одной минуты.'
        ),),
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return (
            f'{self.name} - {self.text[:MAX_TEXT_RECIPES]} - '
            f'{self.author.username} - {self.cooking_time}'
        )


class RecipeIngredient(models.Model):
    """Модель количества ингредиентов в рецепте."""

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        'Количество ингредиентов',
        validators=(MinValueValidator(
            MIN_VALUE_VALIDATOR,
            message='Минимальное количество ингредиентов - 1.'
        ),),
    )

    class Meta:
        verbose_name = 'ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        ordering = ('recipe',)
        default_related_name = 'recipe_ingredient'
        constraints = (
            models.UniqueConstraint(
                name='%(app_label)s_%(class)s_unique_ingredient_in_recipe',
                fields=('recipe', 'ingredient'),
            ),
        )

    def __str__(self):
        return f'{self.recipe} - {self.ingredient} - {self.amount}'


class Favorite(models.Model):
    """Модель избранных рецептов."""

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = (
            models.UniqueConstraint(
                name='%(app_label)s_%(class)s_unique_favorite',
                fields=('user', 'recipe'),
            ),
        )

    def __str__(self):
        return f'{self.user} - {self.recipe}'


class ShoppingCart(models.Model):
    """Модель списка покупок."""

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = (
            models.UniqueConstraint(
                name='%(app_label)s_%(class)s_unique_cart',
                fields=('user', 'recipe'),
            ),
        )

    def __str__(self):
        return f'{self.user} - {self.recipe}'
