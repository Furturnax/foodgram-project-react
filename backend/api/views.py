from django.contrib.auth.models import AnonymousUser
from django.db.models import Exists, OuterRef, Sum
from django.http import FileResponse
from djoser.views import UserViewSet as DjoserUserViewSet
from django_filters import rest_framework as filters
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers import (
    FavoriteSerializer,
    ShoppingCartSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    SubscribeSerializer,
    SubscriptionsSerializer,
    UserSerializer,
    TagSerializer,
)
from core.filters import IngredientFilter, RecipeFilter
from core.permissions import IsAuthorOrReadOnly
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
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
        serializer = SubscriptionsSerializer(
            page,
            context={'request': request},
            many=True,
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=('post',))
    def subscribe(self, request, id):
        """Подписка на пользователя."""
        data = {
            'user': request.user.id,
            'following': id
        }
        serializer = SubscribeSerializer(
            data=data,
            context={'request': request},
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id):
        """Отписка от пользователя."""
        user = request.user
        subscribe_instance = Follow.objects.filter(user=user)
        if subscribe_instance.exists():
            subscribe_instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


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
            'download_shopping_cart',
        ):
            return (permissions.IsAuthenticated(),)
        return (IsAuthorOrReadOnly(),)

    def get_queryset(self):
        """Возвращает подзапросы к рецептам."""
        user = self.request.user

        if isinstance(user, AnonymousUser):
            return Recipe.objects.all()

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

    @staticmethod
    def write_favorite(serializer, pk, request):
        """Статический метод добавления рецепта в избранное."""
        serializer_instance = serializer(
            data={
                'user': request.user.id,
                'recipe': pk
            },
            context={
                'request': request,
                'action_name': 'favorite'
            },
        )
        serializer_instance.is_valid(raise_exception=True)
        serializer_instance.save()
        return serializer_instance.data

    @action(
        detail=True,
        methods=('post',),
        serializer_class=FavoriteSerializer
    )
    def favorite(self, request, pk):
        """Добавление рецепта в избранное."""
        response_data = self.write_favorite(
            self.serializer_class,
            pk,
            request,
        )
        return Response(response_data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def destroy_favorite(self, request, pk):
        """Удаление рецепта из избранного."""
        favorite_instance = Favorite.objects.filter(
            user=request.user,
            recipe=pk,
        )
        if favorite_instance.exists():
            favorite_instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def write_shopping_cart(serializer, pk, request):
        """Статический метод добавления рецепта в список покупок."""
        serializer_instance = serializer(
            data={
                'user': request.user.id,
                'recipe': pk
            },
            context={
                'request': request,
                'action_name': 'shopping_cart'
            },
        )
        serializer_instance.is_valid(raise_exception=True)
        serializer_instance.save()
        return serializer_instance.data

    @action(
        detail=True,
        methods=('post',),
        serializer_class=ShoppingCartSerializer
    )
    def shopping_cart(self, request, pk):
        """Добавление рецепта в список покупок."""
        response_data = self.write_shopping_cart(
            self.serializer_class,
            pk,
            request,
        )
        return Response(response_data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def destroy_shopping_cart(self, request, pk):
        """Удаление рецепта из списка покупок."""
        shopping_cart_instance = ShoppingCart.objects.filter(
            user=request.user,
            recipe=pk,
        )
        if shopping_cart_instance:
            shopping_cart_instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def generate_ingredient_list(ingredient):
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
        lines.extend(self.generate_ingredient_list(
            ingredient
        ) for ingredient in ingredients)
        response.streaming_content = lines
        return response
