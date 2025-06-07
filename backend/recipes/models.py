from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint
from django.utils import timezone
from sqids import Sqids

from foodgram.constants import LENGTH_OF_FIELDS_RECIPES
from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        max_length=LENGTH_OF_FIELDS_RECIPES,
        verbose_name="Название ингредиента",
        db_index=True,
    )
    measurement_unit = models.CharField(
        max_length=LENGTH_OF_FIELDS_RECIPES,
        verbose_name="Единица измерения"
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "measurement_unit"],
                name="unique_name_measurement_unit"
            )
        ]

    def __str__(self):
        return f"{self.name} {self.measurement_unit}"


class Recipe(models.Model):
    short_url = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        blank=True
    )
    author = models.ForeignKey(
        User,
        verbose_name="Автор рецепта",
        on_delete=models.CASCADE,
        related_name="recipes",
    )
    name = models.CharField(
        max_length=LENGTH_OF_FIELDS_RECIPES,
        verbose_name="Название рецепта",
    )
    image = models.ImageField(
        upload_to="recipes/image/",
        verbose_name="Изображение"
    )
    text = models.TextField(verbose_name="Описание")
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name="Ингредиенты",
        through="IngredientRecipe",
        related_name="in_recipes"
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время готовки (минуты)",
        validators=[
            MinValueValidator(
                1, message="Время приготовления не менее 1 минуты."
            ),
            MaxValueValidator(
                1441, message="Время приготовления не более 24 часов."
            ),
        ],
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации",
        auto_now_add=True
    )

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.short_url:
            today = timezone.now()
            keys_for_short_url = [
                round(today.timestamp() * 1000),
                self.author.id,
                self.cooking_time,
            ]
            sqids = Sqids()
            code = sqids.encode(keys_for_short_url)
            self.short_url = code
        return super(Recipe, self).save(*args, **kwargs)


class FavoriteShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
    )

    class Meta:
        abstract = True
        constraints = [
            UniqueConstraint(
                fields=("user", "recipe"),
                name="%(app_label)s_%(class)s_unique"
            )
        ]

    def __str__(self):
        return f"{self.user} :: {self.recipe}"


class Favorite(FavoriteShoppingCart):
    class Meta(FavoriteShoppingCart.Meta):
        default_related_name = "favorites"
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"


class ShoppingCart(FavoriteShoppingCart):
    class Meta(FavoriteShoppingCart.Meta):
        default_related_name = "shopping_list"
        verbose_name = "Корзина"
        verbose_name_plural = "Корзина"


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name="Ингредиент",
        related_name="in_ingredient_recipes"
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепт",
        on_delete=models.CASCADE,
        related_name="ingredient_recipe",
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                1, message="Минимальный вес 1."),
            MaxValueValidator(
                10000, message="Вес превосходит максимум - 10000 .")
        ],
        verbose_name="Количество ингредиента"
    )

    class Meta:
        ordering = ("-id",)
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты рецепта"

    def __str__(self):
        return (
            f"{self.ingredient.name} - {self.ingredient.measurement_unit}"
            f" : {self.amount} "
        )
