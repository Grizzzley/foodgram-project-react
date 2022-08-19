from django.urls import include, path
from rest_framework import routers
from users.views import CustomUserViewSet, SubscribeViewSet

app_name = 'users'

router = routers.DefaultRouter()
router.register('users', CustomUserViewSet)

urlpatterns = [
    path(
        'users/subscriptions/',
        SubscribeViewSet.as_view({'get': 'list'}), name='subscriptions'
    ),
    path(
        'users/<users_id>/subscribe/',
        SubscribeViewSet.as_view(
            {'post': 'create', 'delete': 'delete'}), name='subscribe'
    ),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))
]
