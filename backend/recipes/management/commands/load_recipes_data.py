import base64
import json

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Load recipes from JSON file using ORM and your models"

    def handle(self, *args, **options):
        from recipes.models import Ingredient, IngredientRecipe, Recipe

        self.stdout.write("Starting recipe loading...")

        with open("data/recipes.json", encoding="utf-8") as f:
            data = json.load(f)

        for entry in data:
            email = entry.get("email")
            recipe_data = entry.get("recipe")

            if not email or not recipe_data:
                self.stdout.write(self.style.ERROR(
                    "Missing email or recipe data"
                ))
                continue

            try:
                author = User.objects.get(email=email)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"User {email} not found"))
                continue

            if Recipe.objects.filter(
                    name=recipe_data["name"],
                    author=author).exists():
                self.stdout.write(
                    f"Recipe '{recipe_data['name']}' "
                    f"already exists for {email}"
                )
                continue

            recipe = Recipe(
                name=recipe_data["name"],
                text=recipe_data["text"],
                cooking_time=recipe_data["cooking_time"],
                author=author,
            )

            image_data = recipe_data.get("image")
            if image_data:
                format, imgstr = image_data.split(';base64,')
                ext = format.split('/')[-1]
                img_file = ContentFile(
                    base64.b64decode(imgstr), name=f"{recipe.name}.{ext}"
                )
                recipe.image.save(img_file.name, img_file, save=False)

            recipe.save()

            for ing in recipe_data.get("ingredients", []):
                try:
                    ingredient = Ingredient.objects.get(id=ing["id"])
                except Ingredient.DoesNotExist:
                    self.stdout.write(self.style.ERROR(
                        f"Ingredient with id={ing['id']} not found")
                    )
                    continue

                IngredientRecipe.objects.create(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=ing["amount"],
                )

            self.stdout.write(self.style.SUCCESS(
                f"Recipe '{recipe.name}' created for {email}")
            )

        self.stdout.write(self.style.SUCCESS("Recipe loading complete"))
