#!/bin/sh
./wait-for-it.sh db:5432 --timeout=30 --strict -- echo "Postgres is up"

python manage.py migrate
python manage.py load_ingredients_data
python manage.py load_users_data
python manage.py load_recipes_data
python manage.py collectstatic --no-input
exec gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000
