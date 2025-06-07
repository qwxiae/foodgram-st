## Описание проекта Foodgram
Foodgram – это сервис для публикации рецептов. Авторизованные пользователи могут публиковать свои рецепты, подписываться на других пользователей и добавлять их рецепты в избранное и в покупки. Рецепты, добавленные в покупки, можно скачать в формате списка ингредиентов. Опубликованные рецепты может просмотреть каждый пользователь.
## Технологический стек
[![Python](https://img.shields.io/badge/-Python-464646?style=flat&logo=Python&logoColor=56C0C0&color=008080)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat&logo=Django&logoColor=56C0C0&color=008080)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat&logo=Django%20REST%20Framework&logoColor=56C0C0&color=008080)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat&logo=PostgreSQL&logoColor=56C0C0&color=008080)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat&logo=NGINX&logoColor=56C0C0&color=008080)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat&logo=gunicorn&logoColor=56C0C0&color=008080)](https://gunicorn.org/)
[![Docker](https://img.shields.io/badge/-Docker-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/)
[![Docker-compose](https://img.shields.io/badge/-Docker%20compose-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/)
[![Docker Hub](https://img.shields.io/badge/-Docker%20Hub-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/products/docker-hub)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat&logo=GitHub%20actions&logoColor=56C0C0&color=008080)](https://github.com/features/actions)
## Настройка проекта
- Клонируйте репозиторий с проектом на свой компьютер.
```
git clone https://github.com/clmr-y/foodgram-st.git
```
- Перейдите в папку backend
```
cd backend
```
- Установите и активируйте виртуальное окружение

```
python -m venv venv
```
```
source /venv/bin/activate
```
- Установите зависимости из файла requirements.txt
```
python -m pip install --upgrade pip
```
```
pip install -r requirements.txt
```
- Создайте файл .env в папке infra:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
DEBUG=0
```

- Выполните миграции:
```
python manage.py migrate
```

- Создайте супер пользователя 
```
python manage.py createsuperuser
```

- Загрузите статику:
```
python manage.py collectstatic --no-input
```
- Заполните базу необходимыми данными: 
```
python manage.py load_ingredients_data
```

## Запуск проекта через Docker

Выполните команду:
```
cd ../infra
docker-compose up -d --build
```
