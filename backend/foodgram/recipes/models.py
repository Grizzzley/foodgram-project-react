from django.db import models

from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        max_length=180,
        verbose_name='Ингредиент'
    )
    measurement_unit = models.CharField(
        max_length=10,
        verbose_name='Тип веса'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=180,
        verbose_name='Тег',
        null=False
    )
    color = models.CharField(
        max_length=7,
        unique=True,
        default='#FF0000',
        verbose_name='HEX код'
    )
    slug = models.SlugField(
        unique=True,
        max_length=100,
        verbose_name='Слаг тег'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        'Название рецепта',
        max_length=256,
        db_index=True,
    )
    text = models.TextField(
        'Текст рецепта',
        blank=True,
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Картинка рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингридиенты',
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tag,
        'Теги',
        max_length=100,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipe',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = [models.UniqueConstraint(
            fields=['name', 'author'],
            name='unique_recipe',
        )]
        ordering = ['-pub_date', ]

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe_ingredient',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_recipe',
    )
    amount = models.PositiveSmallIntegerField(
        help_text='Укажите кол-во больше нуля.',
        verbose_name='Вес',
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'], name='unique_ingredientrecipe'
            )
        ]

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'


class RecipesTags(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='tag',
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='recipe',
    )

    class Meta:
        verbose_name = 'Тег в рецепте'
        verbose_name_plural = 'Теги в рецепте'
        ordering = ['-id']

    def __str__(self):
        return f'{self.tag.name}, {self.recipe.name}'


class FavoriteRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='favorite'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorite',
    )
    favorite = models.BooleanField(verbose_name='Избранное', default=False)
    shopping_cart = models.BooleanField(
        verbose_name='Корзина покупок',
        default=False,
    )

    class Meta:
        verbose_name = 'Любимый рецепт'
        verbose_name_plural = 'Любимые рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_favorite_recipe',
            )
        ]
        ordering = ['recipe']

    def __str__(self):
        return f'{self.recipe} {self.user}'


class ShoppingList(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='shopping_carts'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping_user'
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_shopping_cart',
            )
        ]
        ordering = ['recipe']

    def __str__(self):
        return f'{self.user} {self.recipe}'
