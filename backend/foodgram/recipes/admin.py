from django.contrib import admin

from .models import (
    FavoriteRecipe, Ingredient, Recipe, RecipeIngredient,
    ShoppingList
)


@admin.register(Ingredient)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('id', 'ingredient', 'measurement_unit')
    list_display_links = ('id', 'ingredient')
    list_filter = ('ingredient',)
    search_fields = ('ingredient',)


@admin.register(Recipe)
class RecipesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'favorited')
    list_display_links = ('id', 'name')
    list_filter = ('author', 'name', 'tags')
    search_fields = ('name', 'text')

    def favorited(self, obj):
        return FavoriteRecipe.objects.filter(recipe=obj).count()

    favorited.short_description = 'Кол-во любимых рецептов'


@admin.register(FavoriteRecipe)
class RecipesFavoritesAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    list_display_links = ('id',)
    list_filter = ('user', 'recipe')
    search_fields = ('recipe__name',)


@admin.register(RecipeIngredient)
class RecipesIngredientsAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'weight')
    list_display_links = ('id',)
    list_filter = ('recipe',)
    search_fields = ('recipe__name', 'ingredient__name')


@admin.register(ShoppingList)
class ShoppingCartsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    list_display_links = ('id',)
    list_filter = ('user', 'recipe')
    search_fields = ('recipe__name',)
