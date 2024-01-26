import csv

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from django_filters import rest_framework as filters
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from api.serializers import (
    FavoriteRecipeSerializer,
    FollowSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    UserSerializer,
    TagSerializer
)
from core.filters import IngredientFilter, RecipeFilter
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
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
    permission_classes = (IsAdminOrReadOnly,)
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для работы с ингредиентами."""

    http_method_names = ('get',)
    permission_classes = (IsAdminOrReadOnly,)
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
    queryset = Recipe.objects.all()
    pagination_class = None
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

    @action(detail=True, methods=('post', 'delete'))
    def favorite(self, request, pk=None):
        """Добавление и удаление рецепта из избранного."""
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = FavoriteRecipeSerializer(
            recipe, data=request.data,
            context={
                'request': request,
                'action_name': 'favorite'
            }
        )
        serializer.is_valid(raise_exception=True)
        if request.method == 'POST':
            Favorite.objects.create(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        Favorite.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=('post', 'delete'))
    def shopping_cart(self, request, pk=None):
        """Добавление рецепта в список покупок."""
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = FavoriteRecipeSerializer(
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

    @action(detail=False, methods=('get',))
    def download_shopping_cart(self, request):
        """Отдает пользователю список для покупок в виде CSV файла."""
        user = request.user
        shopping_cart = ShoppingCart.objects.filter(user=user).select_related(
            'recipe__ingredients'
        ).values(
            'recipe__ingredients__name',
            'recipe__ingredients__measurement_unit',
            'recipe__recipe_ingredient__amount'
        )
        ingredient_totals = {}
        for item in shopping_cart:
            key = (
                f'{item["recipe__ingredients__name"]} '
                f'({item["recipe__ingredients__measurement_unit"]})'
            )
            if key in ingredient_totals:
                ingredient_totals[key] += item[
                    "recipe__recipe_ingredient__amount"
                ]
            else:
                ingredient_totals[key] = item[
                    "recipe__recipe_ingredient__amount"
                ]
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            'attachment; filename="Shopping_cart.csv"'
        )
        writer = csv.writer(response)
        writer.writerow(['Список ингредиентов для покупки:'])
        for ingredient, amount in ingredient_totals.items():
            writer.writerow([f'{ingredient} - {amount}'])
        return response
