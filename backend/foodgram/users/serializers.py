from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from django.utils.datastructures import MultiValueDictKeyError

from recipes.models import Recipe
from .models import Subscription, User


class CurrentUserDefaultId(object):
    requires_context = True

    def __call__(self, serializer_instance=None):
        if serializer_instance is not None:
            self.user_id = serializer_instance.context['request'].user.id
            return self.user_id


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=self.context['request'].user,
            author=obj
        ).exists()


class SubscriptionRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user:
            return False
        return Subscription.objects.filter(user=user, author=obj).exists()

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj).all()
        try:
            limit = int(self.context['request'].query_params['recipes_limit'])
            recipes = recipes[:limit]
        except MultiValueDictKeyError:
            pass
        return FavoriteRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()
