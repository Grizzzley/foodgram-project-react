from http import HTTPStatus

from djoser.views import UserViewSet
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from django.shortcuts import get_list_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from api.pagination import CustomPagination
from users.models import Subscription, User
from users.serializers import SubscriptionSerializer


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    pagination_class = CustomPagination
    permission_classes = (AllowAny,)

    @action(
        detail=False,
        url_path='subscriptions',
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        user = get_object_or_404(
            User,
            id=request.user.id
        )
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        if pages is not None:
            serializer = SubscriptionSerializer(
                pages,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = SubscriptionSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id):
        user = request.user
        if request.method == 'POST':
            data = {'user': user.id, 'author': id}
            serializer = SubscriptionSerializer(
                data=data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        following = get_object_or_404(User, id=id)
        follow = get_object_or_404(
            Subscription, user=user, author=following
        )
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscribeViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return get_list_or_404(User, following__user=self.request.user)

    def create(self, request, *args, **kwargs):
        user_id = self.kwargs.get('users_id')
        user = get_object_or_404(User, id=user_id)
        Subscription.objects.create(
            user=request.user, following=user
        )
        return Response(HTTPStatus.CREATED)

    def delete(self, request, *args, **kwargs):
        author_id = self.kwargs['users_id']
        user_id = request.user.id
        subscribe = get_object_or_404(
            Subscription, user__id=user_id, following__id=author_id
        )
        subscribe.delete()
        return Response(HTTPStatus.NO_CONTENT)
