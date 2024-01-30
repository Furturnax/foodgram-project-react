from django.db.models import Exists, OuterRef, Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from django_filters import rest_framework as filters
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers import (
    ShortRecipeInFollowSerializer,
    FollowSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    UserSerializer,
    TagSerializer
)
from core.filters import IngredientFilter, RecipeFilter
from core.permissions import IsAuthorOrReadOnly
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag
)
from users.models import Follow, User


class UserViewSet(DjoserUserViewSet):
    """Вьюсет для работы с пользователями."""

    serializer_class = UserSerializer
    queryset = User.objects.all()
    http_method_names = ('get', 'post', 'delete')

    def get_permissions(self):
        """Распределение прав на действия."""
        if self.action in ('me', 'subscriptions', 'subscribe'):
            return (permissions.IsAuthenticated(),)
        return (permissions.AllowAny(),)

    @action(detail=False, methods=('get',))
    def subscriptions(self, request):
        """Просмотр своих подписок."""
        user = self.request.user
        user_following = User.objects.filter(following__user=user)
        page = self.paginate_queryset(user_following)
        serializer = FollowSerializer(
            page, context={'request': request}, many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=('post', 'delete'))
    def subscribe(self, request, id=None):
        """Подписка и отписка от пользователей."""
        user = self.request.user
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            Follow.objects.create(user=user, following=author)
            serializer = FollowSerializer(
                author, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        Follow.objects.filter(user=user, following=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для работы с тегами."""

    http_method_names = ('get',)
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для работы с ингредиентами."""

    http_method_names = ('get',)
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    pagination_class = None
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с рецептами."""

    http_method_names = ('get', 'post', 'patch', 'delete')
    permission_classes = (IsAuthorOrReadOnly,)
    serializer_class = RecipeWriteSerializer
    queryset = (
        Recipe.objects.select_related('author')
        .prefetch_related('ingredients', 'tags').all()
    )
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Определяет класс сериализатора в зависимости от типа запроса."""
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def get_permissions(self):
        """Распределение прав на действия."""
        if self.action in (
            'favorite',
            'shopping_cart',
            'download_shopping_cart'
        ):
            return (permissions.IsAuthenticated(),)
        return (IsAuthorOrReadOnly(),)

    def get_queryset(self):
        """Возвращает подзапросы к рецептам."""
        user = self.request.user
        return (
            Recipe.objects
            .select_related('author')
            .prefetch_related('ingredients', 'tags')
            .annotate(
                is_favorited=Exists(
                    Favorite.objects.filter(
                        user=user,
                        recipe=OuterRef('pk')
                    )
                ),
                is_in_shopping_cart=Exists(
                    ShoppingCart.objects.filter(
                        user=user,
                        recipe=OuterRef('pk')
                    )
                )
            )
            .all()
        )

    @action(detail=True, methods=('post',))
    def favorite(self, request, pk):
        """Добавление рецепта из избранного."""
        recipe = get_object_or_404(Recipe, pk=pk)
        data = {
            'user': request.user.id,
            'recipe': recipe.id
        }
        serializer = ShortRecipeInFollowSerializer(
            data=data,
            context={
                'request': request,
                'action_name': 'favorite'
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def destroy_favorite(self, request, pk):
        favorite_entry = get_object_or_404(
            Favorite,
            user=request.user,
            recipe=get_object_or_404(Recipe, id=pk)
        )
        favorite_entry.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=('post', 'delete'))
    def shopping_cart(self, request, pk=None):
        """Добавление рецепта в список покупок."""
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = ShortRecipeInFollowSerializer(
            recipe, data=request.data,
            context={
                'request': request,
                'action_name': 'shopping_cart'
            }
        )
        serializer.is_valid(raise_exception=True)
        if request.method == 'POST':
            ShoppingCart.objects.create(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        ShoppingCart.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def generate_ingredient_line(ingredient):
        """Генерирует строку с ингредиентом."""
        return (
            f'{ingredient["ingredient__name"]} '
            f'({ingredient["ingredient__measurement_unit"]}) - '
            f'{ingredient["amount"]}\n'
        )

    @action(detail=False, methods=('get',))
    def download_shopping_cart(self, request):
        """Отдает пользователю список для покупок в виде TXT файла."""
        ingredients = RecipeIngredient.objects.filter(
            recipe__shoppingcart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit',
        ).annotate(
            amount=Sum('amount')
        ).order_by('ingredient__name')
        response = FileResponse(content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="Shopping_cart.txt"'
        )
        lines = ['Список ингредиентов для покупки:\n']
        lines.extend(self.generate_ingredient_line(
            ingredient
        ) for ingredient in ingredients)
        response.streaming_content = lines
        return response
