from django.db.models import F
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShippingCart,
    Tag
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
            'password',
            'is_subscribed',
        )
        read_only_fields = ('is_subscribed',)
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """Создает нового пользователя."""
        return User.objects.create_user(**validated_data)

    def get_is_subscribed(self, obj):
        """Проверяет подписку на автора."""
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, following=obj).exists()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор модели тега."""

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )
        read_only_fields = (
            'id',
            'name',
            'color',
            'slug'
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели ингредиента."""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )
        read_only_fields = (
            'id',
            'name',
            'measurement_unit'
        )


class IngredientAmountSerializer(serializers.ModelSerializer):
    """Сериализатор для записи ингредиента и количества в рецепт."""

    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'amount'
        )


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""

    ingredients = IngredientAmountSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()

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
        RecipeIngredient.objects.bulk_create((
            RecipeIngredient(
                recipe=recipe,
                ingredient=get_object_or_404(
                    Ingredient,
                    id=ingredient['id']
                ),
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ),)

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

    def update(self, instance, validated_data):
        """Обновляет существующий рецепт."""
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        instance.tags.set(tags_data)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        self.create_ingredients(instance, ingredients_data)
        instance.save()
        return instance

    def to_representation(self, instance):
        """Возвращает сериализованный экземпляр рецепта."""
        return RecipeReadSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для получения рецепта."""

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

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

    def get_ingredients(self, recipe):
        """Получает ингредиенты рецепта с полем amount."""
        return recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('recipe_ingredient__amount')
        )

    def get_is_favorited(self, obj):
        """Проверяет наличие рецепта в избранном."""
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        """Проверяет наличие рецепта в списке покупок."""
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return ShippingCart.objects.filter(user=user, recipe=obj).exists()


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для получения короткого рецепта в избранном."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
        read_only_fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для подписки на автора."""

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

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
            'recipes_count'
        )
        read_only_fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        """Проверяет подписку на автора."""
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, following=obj).exists()

    def get_recipes(self, obj):
        """Возвращает рецепты автора."""
        recipes_limit = int(self.context['request'].query_params.get(
            'recipes_limit',
            default=2
            )
        )
        recipes = Recipe.objects.filter(author=obj)[:recipes_limit]
        serializer = FavoriteRecipeSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        """Возвращает количество рецептов автора."""
        return Recipe.objects.filter(author=obj).count()
