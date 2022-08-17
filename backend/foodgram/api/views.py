from django.http import HttpResponse
from django.db.models import Sum
from django_filters import rest_framework as filters
from rest_framework import filters as rest_filters
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.filters import RecipeFilter
from api.pagination import CustomPagination
from api.permissions import IsAuthorOrAdminOrReadOnly
from api.serializers import (
    FavoriteRecipeSerializer, IngredientSerializer,
    RecipeSerializer, TagSerializer
)
from recipes.models import (
    FavoriteRecipe, Ingredient, RecipeIngredient,
    Recipe, Tag, ShoppingList
)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.DjangoFilterBackend, rest_filters.SearchFilter)
    filterset_fields = ('ingredient',)
    search_fields = ('^ingredient',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user, tags=self.request.data['tags']
        )

    def perform_update(self, serializer):
        serializer.save(
            author=self.request.user, tags=self.request.data['tags']
        )

    @action(
        methods=['POST', 'DELETE'],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path='(?P<id>[0-9]+)/shopping_cart',
    )
    def shopping_cart(self, request, id):
        recipe_by_id = get_object_or_404(Recipe, id=id)
        if request.method == 'POST':
            favorite_recipe, created = FavoriteRecipe.objects.get_or_create(
                recipe=recipe_by_id, user=self.request.user
            )
            if created is True:
                raise ValidationError(
                    detail={'error': ['Рецепт уже был добавлен.']}
                )
            favorite_recipe.shopping_cart = True
            favorite_recipe.save()
            serializer = FavoriteRecipeSerializer(recipe_by_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        favorite_recipe = get_object_or_404(
            ShoppingList, recipe=recipe_by_id, user=self.request.user
        )
        if not favorite_recipe.shopping_cart:
            raise ValidationError(
                detail={'error': ['Данного рецепта нет в списке покупок.']}
            )
        favorite_recipe.shopping_cart = False
        favorite_recipe.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['POST', 'DELETE'],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path='(?P<id>[0-9]+)/favorite',
    )
    def favorite(self, request, id):
        recipe_by_id = get_object_or_404(Recipe, id=id)
        if request.method == 'POST':
            favorite_recipe, created = FavoriteRecipe.objects.get_or_create(
                recipe=recipe_by_id, user=self.request.user
            )
            if created is True:
                raise ValidationError(
                    detail={'error': ['Рецепт уже был добавлен в избранные.']}
                )
            favorite_recipe.favorite = True
            favorite_recipe.save()
            serializer = FavoriteRecipeSerializer(recipe_by_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        favorite_recipe = get_object_or_404(
            FavoriteRecipe, recipe=recipe_by_id, user=self.request.user
        )
        if not favorite_recipe.shopping_cart:
            raise ValidationError(
                detail={'error': ['Данного рецепта нет в избранных.']}
            )
        favorite_recipe.favorite = False
        favorite_recipe.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_carts__user=user
        ).order_by(
            'ingredient__name'
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit',
        ).annotate(sum_amount=Sum('amount'))
        shopping_cart = '\n'.join([
            f'{ingredient["ingredient__name"]} - {ingredient["sum_amount"]}'
            f'{ingredient["ingredient__measurement_unit"]}'
            for ingredient in ingredients
        ])
        filename = 'shopping_cart.txt'
        response = HttpResponse(shopping_cart, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
