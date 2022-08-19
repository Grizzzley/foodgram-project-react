from django.contrib import admin

from users.models import Subscription, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    fields = (
        'username',
        'email',
        'role',
        'first_name',
        'last_name',
        'blocked',
    )
    list_display = (
        'pk',
        'username',
        'first_name',
        'last_name',
        'email',
        'is_staff',
        'is_blocked',
    )
    list_display_links = (
        'pk',
        'username',
    )
    list_filter = (
        'username',
        'email',
        ('is_staff', admin.BooleanFieldListFilter),
    )
    search_fields = (
        'username',
        'first_name',
        'last_name',
    )
    empty_value_display = '-пусто-'
    list_per_page = 10
    list_max_show_all = 100
    readonly_fields = ('id',)

    def is_blocked(self, obj):
        return obj.is_blocked

    is_blocked.boolean = True


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'author',
    )
    search_fields = ('author', )
