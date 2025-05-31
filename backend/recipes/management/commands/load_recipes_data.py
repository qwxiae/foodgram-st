import json
import requests
import base64
from io import BytesIO
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create recipes via API"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Starting recipe creation"))

        with open("data/recipes.json", encoding="utf-8") as file:
            data = json.load(file)

        for entry in data:
            login_data = {
                "email": entry["email"],
                "password": entry["password"]
            }
            auth_response = requests.post(
                "http://127.0.0.1:8000/api/auth/token/login/", data=login_data
            )

            if auth_response.status_code != 200:
                self.stdout.write(
                    self.style.ERROR(f"Login failed for {entry['email']}")
                )
                continue

            token = auth_response.json()["auth_token"]
            headers = {"Authorization": f"Token {token}"}

            recipe = entry["recipe"]

            image_data = recipe["image"].split(",")[1]
            image_content = base64.b64decode(image_data)
            image_file = BytesIO(image_content)
            image_file.name = "image.png"

            ingredients = recipe["ingredients"]

            files = {
                "image": ("image.png", image_file, "image/png"),
            }

            data = {
                "name": recipe["name"],
                "text": recipe["text"],
                "cooking_time": recipe["cooking_time"],
            }

            for i, ingredient in enumerate(ingredients):
                data[f"ingredients[{i}][id]"] = ingredient["id"]
                data[f"ingredients[{i}][amount]"] = ingredient["amount"]

            recipe_response = requests.post(
                "http://127.0.0.1:8000/api/recipes/",
                data=data,
                files=files,
                headers=headers,
            )

            if recipe_response.status_code == 201:
                self.stdout.write(
                    self.style.SUCCESS(f"Recipe created for {entry['email']}")
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f"Failed to create recipe for {entry['email']} - "
                        f"{recipe_response.content.decode()}"
                    )
                )
