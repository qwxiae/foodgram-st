from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User, Follow
from recipes.models import Recipe, Ingredient, Favorite, ShoppingCart
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image


def create_user(**kwargs):
    if 'username' not in kwargs:
        kwargs['username'] = kwargs.get(
            'email', 'user@example.com'
        ).split('@')[0]
    return User.objects.create_user(**kwargs)


def create_recipe(author, name="Sample"):
    return Recipe.objects.create(author=author, name=name, cooking_time=10)


def create_image():
    img = BytesIO()
    Image.new("RGB", (100, 100)).save(img, format='JPEG')
    img.seek(0)
    return SimpleUploadedFile(
        "test.jpg",
        img.read(),
        content_type="image/jpeg"
    )


class UserTests(APITestCase):
    def setUp(self):
        self.user = create_user(
            username="test",
            email="test@example.com",
            password="pass1234"
        )
        self.author = create_user(
            username="author",
            email="author@example.com",
            password="pass1234"
        )
        self.client.force_authenticate(self.user)

    def test_get_me(self):
        url = "/api/users/me/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)

    def test_subscribe_and_unsubscribe(self):
        url = f"/api/users/{self.author.id}/subscribe/"
        self.assertEqual(Follow.objects.count(), 0)

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Follow.objects.count(), 1)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Follow.objects.count(), 0)

    def test_avatar_upload_and_delete(self):
        url = "/api/users/me/avatar/"
        image = create_image()

        response = self.client.put(url, {"avatar": image}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class RecipeTests(APITestCase):
    def setUp(self):
        self.user = create_user(email="user@example.com", password="test1234")
        self.recipe = create_recipe(self.user)
        self.client.force_authenticate(self.user)

    def test_add_to_favorites(self):
        url = f"/api/recipes/{self.recipe.pk}/favorite/"
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Favorite.objects.filter(
            user=self.user,
            recipe=self.recipe).exists()
        )

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_add_to_shopping_cart(self):
        url = f"/api/recipes/{self.recipe.pk}/shopping_cart/"
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ShoppingCart.objects.filter(
            user=self.user,
            recipe=self.recipe).exists()
        )

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class DownloadCartTest(APITestCase):
    def setUp(self):
        self.user = create_user(email="down@example.com", password="pass1234")
        self.recipe = create_recipe(self.user)
        self.ingredient = Ingredient.objects.create(
            name="Salt",
            measurement_unit="g"
        )
        self.recipe.ingredients.add(
            self.ingredient,
            through_defaults={"amount": 10}
        )
        ShoppingCart.objects.create(user=self.user, recipe=self.recipe)
        self.client.force_authenticate(self.user)

    def test_download_cart(self):
        url = "/api/recipes/download_shopping_cart/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "text/plain")
        self.assertIn("Купить в магазине:", response.content.decode("utf-8"))


class IngredientTest(APITestCase):
    def setUp(self):
        Ingredient.objects.create(name="Sugar", measurement_unit="g")
        Ingredient.objects.create(name="Salt", measurement_unit="g")

    def test_search_ingredient(self):
        url = "/api/ingredients/?search=Su"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Sugar")
