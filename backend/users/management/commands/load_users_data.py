import json

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Загрузить пользователей из JSON-файла"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Старт загрузки пользователей"))

        with open("data/users.json", encoding="utf-8") as f:
            user_data = json.load(f)

        for user_dict in user_data:
            email = user_dict["email"]
            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(
                    username=user_dict["username"],
                    email=user_dict["email"],
                    first_name=user_dict["first_name"],
                    last_name=user_dict["last_name"],
                    password=user_dict["password"],
                )
                self.stdout.write(
                    self.style.SUCCESS(f"Пользователь {email} создан")
                )
            else:
                self.stdout.write(f"Пользователь {email} уже существует")

        self.stdout.write(self.style.SUCCESS(
            "Загрузка пользователей завершена"
        ))
