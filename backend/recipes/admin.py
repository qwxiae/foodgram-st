from django.contrib import admin
from .models import (Favorite, Ingredient, IngredientRecipe,
                     Recipe, ShoppingCart)


class IngredientInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 3
    min_num = 1
    verbose_name = "Ингредиент рецепта"
    verbose_name_plural = "Ингредиенты рецепта"


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "author",
        "name",
        "cooking_time",
        "favorites_count",
        "ingredients_list",
    )
    search_fields = ("name", "author")
    list_filter = ("author", "name")
    inlines = (IngredientInline,)
    empty_value_display = "[пусто]"

    def favorites_count(self, obj):
        return obj.favorites.count()
    favorites_count.short_description = "Избранное"

    def ingredients_list(self, obj):
        return ", ".join(
            [ingredients.name for ingredients in obj.ingredients.all()]
        )
    ingredients_list.short_description = "Ингридиенты"


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    search_fields = ("name",)
    list_filter = ("name",)
    empty_value_display = "[пусто]"


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")
    list_filter = ("user", "recipe")
    search_fields = ("user", "recipe")
    empty_value_display = "[пусто]"


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ("recipe", "user")
    list_filter = ("recipe", "user")
    search_fields = ("user",)
    empty_value_display = "[пусто]"
