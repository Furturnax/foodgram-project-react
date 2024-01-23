from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.permissions import IsSubscribed
from api.serializers import (
    FollowSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    UserSerializer,
    TagSerializer
)
from core.filters import IngredientFilter
from recipes.models import Ingredient, Recipe, Tag
from users.models import Follow, User


class UserViewSet(DjoserUserViewSet):
    """Вьюсет для работы с пользователями."""

    serializer_class = UserSerializer
    queryset = User.objects.all()
    http_method_names = ('get', 'post', 'delete')

    def get_permissions(self):
        """Распределение прав на действия."""
        if self.request.method == 'DELETE':
            return (IsSubscribed(),)
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
    serializer_class = RecipeWriteSerializer
    queryset = Recipe.objects.all()
    pagination_class = None

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeWriteSerializer
