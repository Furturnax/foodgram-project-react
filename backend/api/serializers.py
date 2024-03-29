from django.db import transaction
from django.db.models import F
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from core.consts import MAX_VALUE_VALIDATOR, MIN_VALUE_VALIDATOR
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from users.models import Follow, User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор модели пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        """Проверяет подписку на автора."""
        user = self.context['request'].user
        return (
            user.is_authenticated
            and obj.following.filter(user=user).exists()
        )


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор модели тега."""

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )
        read_only_fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели ингредиента."""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )
        read_only_fields = (
            'id',
            'name',
            'measurement_unit',
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для записи ингредиента и количества в рецепт."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(
        min_value=MIN_VALUE_VALIDATOR,
        max_value=MAX_VALUE_VALIDATOR,
        error_messages={
            'min_value': 'Минимальное количество ингредиентов {limit_value}.',
            'max_value': 'Максимальное количество ингредиентов {limit_value}.',
        }
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'amount',
        )


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""

    ingredients = RecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    image = Base64ImageField(
        allow_null=False,
        allow_empty_file=False,
    )
    cooking_time = serializers.IntegerField(
        min_value=MIN_VALUE_VALIDATOR,
        max_value=MAX_VALUE_VALIDATOR,
        error_messages={
            'min_value': 'Минимальное время приготовления {limit_value}.',
            'max_value': 'Максимальное время приготовления {limit_value}.',
        }
    )

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    @staticmethod
    def create_ingredients(recipe, ingredients):
        """Создает список ингредиентов рецепта."""
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
            )
            for ingredient in ingredients
        ])

    @transaction.atomic
    def create(self, validated_data):
        """Создает новый рецепт."""
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )
        recipe.tags.set(tags_data)
        self.create_ingredients(recipe, ingredients_data)
        recipe.save()
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        """Обновляет существующий рецепт."""
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        instance.tags.set(tags_data)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        self.create_ingredients(instance, ingredients_data)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Возвращает сериализованный экземпляр рецепта."""
        return RecipeReadSerializer(
            instance,
            context=self.context,
        ).data


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для получения рецепта."""

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.BooleanField(default=False)
    is_in_shopping_cart = serializers.BooleanField(default=False)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_ingredients(self, obj):
        """Получает ингредиенты рецепта с полем amount."""
        return obj.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('recipe_ingredient__amount'),
        )


class ShortRecipeInFollowSerializer(serializers.ModelSerializer):
    """Сериализатор для получения короткого рецепта в подписках."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
        read_only_fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class SubscriptionsSerializer(UserSerializer):
    """Сериализатор подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='recipes.count')

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):
        """Возвращает рецепты автора."""
        try:
            recipes_limit = int(
                self.context['request'].query_params.get(
                    'recipes_limit',
                    default=3,
                )
            )
        except ValueError:
            recipes_limit = None
        recipes = obj.recipes.all()[:recipes_limit]
        return ShortRecipeInFollowSerializer(
            recipes,
            many=True,
            context=self.context,
        ).data


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор подписки на пользователя."""

    class Meta:
        model = Follow
        fields = ('user', 'following')

    def validate(self, data):
        """Проверяет подписку на самого себя."""
        user = self.context['request'].user
        following_user = data['following']
        if user == following_user:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.'
            )
        if user.following.filter(
            user=user,
            following=following_user
        ).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя.'
            )
        return data

    def to_representation(self, instance):
        """Возвращает сериализованный экземпляр подписки."""
        return SubscriptionsSerializer(
            instance.following,
            context=self.context,
        ).data


class FavoriteShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для получения рецепта в избранном или корзине."""

    class Meta:
        abstract = True
        fields = ('user', 'recipe',)

    def validate(self, data):
        """Проверяет рецепт в избранном и корзине."""
        user = self.context['request'].user
        recipe = data['recipe']
        if self.Meta.model.objects.filter(
            user=user,
            recipe=recipe
        ).exists():
            raise serializers.ValidationError(
                f'Рецепт уже добавлен в {self.Meta.model._meta.verbose_name}!'
            )
        return data

    def to_representation(self, instance):
        """Возвращает сериализованный экземпляр рецепта."""
        return ShortRecipeInFollowSerializer(
            instance.recipe,
            context=self.context,
        ).data


class FavoriteSerializer(FavoriteShoppingCartSerializer):
    """Сериализатор для добавления рецепта в избранное."""

    class Meta(FavoriteShoppingCartSerializer.Meta):
        model = Favorite


class ShoppingCartSerializer(FavoriteShoppingCartSerializer):
    """Сериализатор для добавления рецепта в список покупок."""

    class Meta(FavoriteShoppingCartSerializer.Meta):
        model = ShoppingCart
