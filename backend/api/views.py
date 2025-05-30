from django.db.models import Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from djoser.views import UserViewSet

from recipes.models import Favorite, Ingredient, IngredientRecipe, Recipe, ShoppingCart
from users.models import Follow, User

from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import AuthorPermission
from .serializers import (
    UserAvatarSerializer,
    WriteRecipeSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    ShoppingCartSerializer,
    SubscribeListSerializer,
    UserSerializer,
)
from rest_framework import mixins, viewsets

class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (IngredientFilter,)
    search_fields = ("^name",)
    pagination_class = None

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = WriteRecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, AuthorPermission]
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def update(self, request, *args, **kwargs):
        if "ingredients" not in request.data or not request.data["ingredients"]:
            return Response(
                {"ingredients": ["Это поле не может быть путсым."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().update(request, *args, **kwargs)

    @staticmethod
    def send_message(ingredients):
        shopping_list = "Купить в магазине:"
        for ingredient in ingredients:
            shopping_list += (
                f"\n{ingredient['ingredient__name']} "
                f"({ingredient['ingredient__measurement_unit']}) - "
                f"{ingredient['amount']}"
            )
        file = "shopping_list.txt"
        response = HttpResponse(shopping_list, content_type="text/plain")
        response["Content-Disposition"] = f'attachment; filename="{file}.txt"'
        return response

    @action(detail=False, methods=["GET"])
    def download_shopping_cart(self, request):
        ingredients = (
            IngredientRecipe.objects.filter(recipe__shopping_list__user=request.user)
            .order_by("ingredient__name")
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(amount=Sum("amount"))
        )
        return self.send_message(ingredients)

    @action(methods=("GET",), detail=True, url_path="get-link")
    def get_link(self, request, pk=None):
        """Получение короткой ссылки на рецепт."""
        recipe = self.get_object()
        short_link = request.build_absolute_uri(f"/s/{recipe.short_url}/")
        data = {"short-link": short_link}
        return Response(data, status=status.HTTP_200_OK)


class FavoriteViewSet(mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        recipe_id = self.kwargs["pk"]
        recipe = get_object_or_404(Recipe, id=recipe_id)
        serializer.save(recipe=recipe)

    def destroy(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        favorite = Favorite.objects.filter(user=request.user, recipe=recipe).first()
        if not favorite:
            return Response({"detail": "Рецепт не был добавлен в избранное"}, status=400)
        favorite.delete()
        return Response(status=204)



class ShoppingCartViewSet(mixins.CreateModelMixin,
                          mixins.DestroyModelMixin,
                          viewsets.GenericViewSet):
    serializer_class = ShoppingCartSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        recipe_id = self.kwargs["pk"]
        recipe = get_object_or_404(Recipe, id=recipe_id)
        serializer.save(recipe=recipe)

    def destroy(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        cart_item = ShoppingCart.objects.filter(user=request.user, recipe=recipe).first()
        if not cart_item:
            return Response({"detail": "Рецепт не добавлен в корзину"}, status=400)
        cart_item.delete()
        return Response(status=204)



class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPagination
    permission_classes = [AllowAny]

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=(
            "PUT",
            "DELETE",
        ),
        url_path="me/avatar",
        permission_classes=(IsAuthenticated,),
    )
    def avatar(self, request):
        user = self.request.user
        if request.method == "PUT":
            serializer = UserAvatarSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {"avatar": request.build_absolute_uri(user.avatar.url)},
                status=status.HTTP_200_OK,
            )

        self.request.user.avatar = None
        self.request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )

    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, pk=id)

        if request.method == "POST":
            serializer = SubscribeListSerializer(
                author, data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "DELETE":
            follow_instance = Follow.objects.filter(user=user, author=author).first()
            if not follow_instance:
                return Response(
                    {"errors": "Подписка не существует."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            follow_instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeListSerializer(
            pages, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)
