from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import (
    RegexValidator
)

USER = 'user'
ADMIN = 'admin'
BLOCK = 'Block'
UNBLOCK = 'Unblock'

ROLES = [
    (USER, 'user'),
    (ADMIN, 'admin'),
]
BLOCK_STATUS = [
    (BLOCK, 'block'),
    (UNBLOCK, 'unblock'),
]


class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Имя пользователя',
        validators=[RegexValidator(r'^[\w.@+-]+')]
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        blank=False,
        verbose_name='Эл. почта'
    )
    first_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Фамилия'
    )
    is_subscribed = models.BooleanField(
        default=False,
        verbose_name='Подписка на данного пользователя',
        help_text='Отметьте для подписки на данного пользователя'
    )
    blocked = models.CharField(
        max_length=10,
        verbose_name='Блокировка',
        choices=BLOCK_STATUS,
        default=UNBLOCK,
    )
    role = models.CharField(
        max_length=5,
        verbose_name='Роли',
        choices=ROLES,
        default=USER,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']

    @property
    def is_admin(self):
        return self.is_superuser or self.role == ADMIN

    @property
    def is_user(self):
        return self.role == USER

    @property
    def is_blocked(self):
        return self.blocked == BLOCK

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=['email', 'username'], name='unique_email_username'
            )
        ]
        ordering = ['id']

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор рецепта',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='user_author_subscribe',
            )
        ]
        ordering = ['id']

    def __str__(self):
        return f'{self.user} - {self.author}'
