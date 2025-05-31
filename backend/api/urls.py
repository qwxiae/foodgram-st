from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, RecipeViewSet, UserViewSet,
                    FavoriteViewSet, ShoppingCartViewSet)

app_name = "api"

router = DefaultRouter()
router.register("ingredients", IngredientViewSet, basename="ingredients")
router.register("recipes", RecipeViewSet, basename="recipes")
router.register("users", UserViewSet, basename="users")


urlpatterns = [
    path("", include(router.urls)),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
    path("recipes/<int:pk>/favorite/", FavoriteViewSet.as_view(
        {"post": "create", "delete": "destroy"}),
        name="favorite"
    ),
    path("recipes/<int:pk>/shopping_cart/", ShoppingCartViewSet.as_view(
        {"post": "create", "delete": "destroy"}),
        name="shopping_cart"
    ),
]
