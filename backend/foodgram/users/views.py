from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
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
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            if self.request.user == author:
                return Response(
                    {'errors': 'Вы не можете подписываться на самого себя.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if Subscription.objects.filter(
                    author=author, user=self.request.user
            ).exists():
                return Response(
                    {'errors': 'Вы уже подписаны на данного пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Subscription.objects.create(author=author, user=self.request.user)
            serializer = SubscriptionSerializer(
                author, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.user == author:
            return Response(
                {'errors': 'Вы не можете отписываться от самого себя.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        follow = Subscription.objects.filter(
            author=author, user_id=self.request.user
        )
        if not follow.exists():
            return Response(
                {'errors': 'Вы не подписаны на данного пользователя.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
