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
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id):
        """Отписка от пользователя."""
        user = request.user
        subscribe_instance = Follow.objects.filter(user=user, following=id)
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
        queryset = Recipe.objects.select_related(
            'author'
        ).prefetch_related(
            'ingredients',
            'tags'
        )
        if isinstance(user, AnonymousUser):
            return Recipe.objects.all()
        return queryset.annotate(
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

    @staticmethod
    def write_recipe(serializer, pk, request):
        """Статический метод записи рецепта."""
        serializer_instance = serializer(
            data={
                'user': request.user.id,
                'recipe': pk
            },
            context={
                'request': request
            },
        )
        serializer_instance.is_valid(raise_exception=True)
        serializer_instance.save()
        return Response(
            serializer_instance.data,
            status=status.HTTP_201_CREATED
        )

    @staticmethod
    def destroy_recipe(model, pk, request):
        """Статический метод удаления рецепта."""
        queryset = model.objects.filter(
            user=request.user,
            recipe=pk,
        )
        if queryset.exists():
            queryset.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=('post',),
        serializer_class=FavoriteSerializer
    )
    def favorite(self, request, pk):
        """Добавление рецепта в избранное."""
        return self.write_recipe(self.serializer_class, pk, request)

    @favorite.mapping.delete
    def destroy_favorite(self, request, pk):
        """Удаление рецепта из избранного."""
        return self.destroy_recipe(Favorite, pk, request)

    @action(
        detail=True,
        methods=('post',),
        serializer_class=ShoppingCartSerializer
    )
    def shopping_cart(self, request, pk):
        """Добавление рецепта в список покупок."""
        return self.write_recipe(self.serializer_class, pk, request)

    @shopping_cart.mapping.delete
    def destroy_shopping_cart(self, request, pk):
        """Удаление рецепта из списка покупок."""
        return self.destroy_recipe(ShoppingCart, pk, request)

    @staticmethod
    def generate_ingredient_list(ingredients):
        """Генерирует список с ингредиентами из строк."""
        lines = ['Список ингредиентов для покупки:\n']
        for ingredient in ingredients:
            lines.append(
                f'{ingredient["ingredient__name"]} '
                f'({ingredient["ingredient__measurement_unit"]}) - '
                f'{ingredient["amount"]}\n'
            )
        content = ''.join(lines)
        return content

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
        content = self.generate_ingredient_list(ingredients)
        return FileResponse(
            content, content_type='text/plain',
            filename="Shopping_cart.txt"
        )
