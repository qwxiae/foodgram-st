import json
import requests

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create recipes via API'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Starting recipe creation'))

        with open('data/recipes.json', encoding='utf-8') as file:
            data = json.load(file)

        for entry in data:
            login_data = {
                "email": entry["email"],
                "password": entry["password"]
            }
            auth_response = requests.post("http://127.0.0.1:8000/api/auth/token/login/", data=login_data)

            if auth_response.status_code != 200:
                self.stdout.write(self.style.ERROR(f"Login failed for {entry['email']}"))
                continue

            token = auth_response.json()["auth_token"]
            headers = {"Authorization": f"Token {token}"}

            recipe_response = requests.post(
                "http://127.0.0.1:8000/api/recipes/",
                json=entry["recipe"],
                headers=headers
            )

            if recipe_response.status_code == 201:
                self.stdout.write(self.style.SUCCESS(f"Recipe created for {entry['email']}"))
            else:
                self.stdout.write(self.style.ERROR(
                    f"Failed to create recipe for {entry['email']} - {recipe_response.content.decode()}"
                ))
