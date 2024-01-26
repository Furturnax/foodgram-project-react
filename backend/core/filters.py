from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe


class IngredientFilter(filters.FilterSet):
    """Фильтр для ингредиентов."""

    name = filters.CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    """Фильтр для полученяи рецептов."""
    author = filters.CharFilter(
        field_name='author__username'
    )
    tags = filters.CharFilter(
        field_name='tags__slug'
    )
    is_favorited = filters.BooleanFilter(
        method='get_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'author',
            'tags',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def get_is_favorited(self, queryset, name, value):
        """Проверяет наличие рецепта в избранном."""
        if value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        """Проверяет наличие рецепта в списке покупок."""
        if value:
            return queryset.filter(cart__user=self.request.user)
        return queryset
