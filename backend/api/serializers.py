from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.fields import SerializerMethodField
from rest_framework.exceptions import ValidationError
from djoser.serializers import (
    UserCreateSerializer as
    BaseUserCreateSerializer,
    UserSerializer
)
from drf_extra_fields.fields import Base64ImageField

from api.fields import Base64ImageFieldSerializer
from users.models import User
from recipes.models import (Favorite, Ingredient, IngredientRecipe,
                            Recipe, ShoppingCart)


class UserAvatarSerializer(UserSerializer):
    avatar = Base64ImageFieldSerializer(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ("avatar",)

    def validate(self, data):
        if "avatar" not in data:
            raise serializers.ValidationError("Поле avatar обязательно.")
        return data


class UserSerializer(UserAvatarSerializer):
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_subscribed",
            "avatar",
        )

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        return obj.following.filter(user=request.user).exists()


class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta:
        model = User
        fields = (
            "id", "email", "username",
            "first_name", "last_name",
            "password"
        )


class SubscribeListSerializer(UserSerializer):
    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ("recipes_count", "recipes")
        read_only_fields = (
            "email", "avatar", "username",
            "first_name", "last_name"
        )

    def validate(self, data):
        request = self.context.get("request")
        parser_context = request.parser_context if request else {}
        kwargs = parser_context.get("kwargs", {})
        author_id = kwargs.get("id")

        author = get_object_or_404(User, id=author_id)
        user = self.context.get("request").user

        if user.follower.filter(author=author_id).exists():
            raise ValidationError(
                detail="Подписка существует.",
                code=status.HTTP_400_BAD_REQUEST,
            )
        if user == author:
            raise ValidationError(
                detail="Нельзя подписаться на себя.",
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get("request")
        limit = request.GET.get("recipes_limit")
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[: int(limit)]
        serializer = RecipeShortSerializer(recipes, many=True, read_only=True)
        return serializer.data


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            "id",
            "name",
            "measurement_unit",
        )


class IngredientRecipeReadSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = IngredientRecipe
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )


class IngredientRecipeWriteSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ("id", "amount")


class RecipeReadSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True, many=False)
    ingredients = IngredientRecipeReadSerializer(
        many=True,
        source="ingredient_recipe"
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(max_length=None)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_ingredients(self, obj):
        ingredients = IngredientRecipe.objects.filter(recipe=obj)
        return IngredientRecipeReadSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        return obj.favorites.filter(user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        return obj.shopping_list.filter(user=request.user).exists()


class WriteRecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientRecipeWriteSerializer(many=True)
    image = Base64ImageField(max_length=None, required=True)
    author = UserSerializer(read_only=True)
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError("Изображение отсутствует.")
        return value

    def validate_cooking_time(self, cooking_time):
        if cooking_time < 1:
            raise serializers.ValidationError(
                "Время готовки не меньше одной минуты."
            )
        elif cooking_time > 1440:
            raise serializers.ValidationError(
                "Время готовки не больше одного дня."
            )
        return cooking_time

    def validate_ingredients(self, ingredients):
        ingredients_set = set()
        if not ingredients:
            raise serializers.ValidationError("Ингрeдиенты отсутствуют.")
        for ingredient in ingredients:
            if ingredient["id"] in ingredients_set:
                raise serializers.ValidationError(
                    "Ингредиенты должны быть уникальны."
                )
            ingredients_set.add(ingredient["id"])
            if int(ingredient.get("amount")) < 1:
                raise serializers.ValidationError(
                    "Количество ингредиента должно быть больше 0."
                )
        return ingredients

    @staticmethod
    def create_ingredients(recipe, ingredients):
        ingredient_list = []
        for ingredient_data in ingredients:
            ingredient_list.append(
                IngredientRecipe(
                    ingredient=ingredient_data["id"],
                    amount=ingredient_data["amount"],
                    recipe=recipe,
                )
            )

        IngredientRecipe.objects.bulk_create(ingredient_list)

    def create(self, validated_data):
        request = self.context.get("request", None)
        ingredients = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        IngredientRecipe.objects.filter(recipe=instance).delete()
        ingredients = validated_data.pop("ingredients")
        self.create_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance, context={"request": self.context.get("request")}
        ).data


class RecipeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class BaseRecipeActionSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        recipe = validated_data.get('recipe')

        related_manager = getattr(user, self.related_name, None)
        if related_manager and related_manager.filter(recipe=recipe).exists():
            raise serializers.ValidationError(self.error_message)

        return self.Meta.model.objects.create(user=user, recipe=recipe)

    def to_representation(self, instance):
        request = self.context.get("request")
        return RecipeShortSerializer(
            instance.recipe,
            context={"request": request}
        ).data


class FavoriteSerializer(BaseRecipeActionSerializer):
    related_name = "favorites"
    error_message = "Рецепт уже добавлен в избранное."

    user = serializers.PrimaryKeyRelatedField(read_only=True)
    recipe = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Favorite
        fields = ("user", "recipe")


class ShoppingCartSerializer(BaseRecipeActionSerializer):
    related_name = "shopping_list"
    error_message = "Рецепт уже добавлен в корзину."

    user = serializers.PrimaryKeyRelatedField(read_only=True)
    recipe = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ShoppingCart
        fields = ("user", "recipe")
