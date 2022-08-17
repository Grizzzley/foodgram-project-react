from django.contrib import admin
from django.urls import include, path


api_patterns = [
    path('', include('api.urls', namespace='api')),
    path('', include('users.urls', namespace='api_users')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(api_patterns)),
]
