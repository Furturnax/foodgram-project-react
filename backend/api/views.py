from django_filters import rest_framework as filters
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import permissions, viewsets

from api.serializers import IngredientSerializer, UserSerializer, TagSerializer
from core.filters import IngredientFilter
from recipes.models import Ingredient, Tag
from users.models import User


class UserViewSet(DjoserUserViewSet):
    """Вьюсет для работы с пользователями."""

    serializer_class = UserSerializer
    queryset = User.objects.all()
    http_method_names = ('get', 'post', 'delete')

    def get_permissions(self):
        """Дает доступ аутентифицированным пользователям."""

        if self.action in ('me',):
            return (permissions.IsAuthenticated(),)
        return (permissions.AllowAny(),)


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
