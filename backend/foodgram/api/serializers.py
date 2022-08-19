from urllib import request

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (
    FavoriteRecipe, Ingredient, RecipeIngredient, Recipe,
    RecipesTags, Tag
)
from users.models import User
from users.serializers import CustomUserSerializer

MIN_AMOUNT = 1


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'ingredient', 'measurement_unit')


class IngredientsInRecipesSerialize(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    ingredient = serializers.ReadOnlyField(source='ingredient.ingredient')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'ingredient', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(
        read_only=True, default=serializers.CurrentUserDefault()
    )
    image = Base64ImageField()
    tags = TagSerializer(read_only=True, many=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'

        validators = [
            UniqueTogetherValidator(
                queryset=Recipe.objects.all(),
                fields=('name', 'author'),
                message='Вы уже добавляли рецепт с данным именем',
            )
        ]

    def get_is_favorited(self, obj):
        user = get_object_or_404(User, username=request.user.username)
        if user.is_anonymous:
            return False
        recipe = FavoriteRecipe.objects.filter(
            user__id=user.id, recipe__id=obj.id
        ).first()
        return recipe.favorite if recipe else False

    def get_is_in_shopping_cart(self, obj):
        user = get_object_or_404(User, username=request.user.username)
        if user.is_anonymous:
            return False
        recipe = FavoriteRecipe.objects.filter(
            user__id=user.id, recipe__id=obj.id
        ).first()
        return recipe.shopping_cart if recipe else False

    def get_ingredients(self, obj):
        qs = RecipeIngredient.objects.filter(recipe=obj)
        return IngredientsInRecipesSerialize(qs, many=True).data

    def validate(self, data):
        if 'ingredients' not in self.initial_data:
            raise serializers.ValidationError(
                {'error': 'Отсутствует информация об ингредиентах'}
            )
        if 'tags' not in self.initial_data:
            raise serializers.ValidationError(
                {'error': 'Отсутствуют теги'}
            )
        lst_unique_ingredients = []
        for ingredient_item in self.initial_data['ingredients']:
            try:
                ingredient = get_object_or_404(
                    Ingredient, id=ingredient_item.id
                )
            except ObjectDoesNotExist:
                raise serializers.ValidationError(
                    {'error': 'Данного ингредиента нет в базе'}
                )
            if int(ingredient_item['amount']) < MIN_AMOUNT:
                raise serializers.ValidationError(
                    {
                        'amount': 'Введите значение больше еденицы'
                    }
                )
            if ingredient in lst_unique_ingredients:
                raise serializers.ValidationError(
                    {'error': 'Ингредиенты уже есть в рецепте'}
                )
            lst_unique_ingredients.append(ingredient)
        data['ingredients'] = self.initial_data['ingredients']
        tags_ids = Tag.objects.all().values_list('id', flat=True)
        unexp_tags_ids = [
            idx for idx in self.initial_data['tags'] if idx not in tags_ids
        ]
        if unexp_tags_ids:
            raise ValidationError(
                detail={
                    'tags': [f'{unexp_tags_ids} - данных тегов нет в базе']
                }
            )
        return data

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.ingredients.clear()
        instance.tags.clear()

        ingredients = validated_data.pop('ingredients')
        tags_ids = validated_data.pop('tags')
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=get_object_or_404(
                    Ingredient, id=ingredient.id
                ),
                amount=ingredient['amount'],
            )
        for tags_id in tags_ids:
            RecipesTags.objects.create(
                recipe=instance,
                tag=get_object_or_404(Tag, id=tags_id),
            )
        return super().update(instance, validated_data)

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags_ids = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            RecipeIngredient.objects.update_or_create(
                recipe=recipe,
                ingredient=get_object_or_404(
                    Ingredient, id=ingredient.id
                ),
                amount=ingredient['amount'],
            )
        for tags_id in tags_ids:
            RecipesTags.objects.update_or_create(
                recipe=recipe,
                tag=get_object_or_404(Tag, id=tags_id)
            )
        return recipe


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
