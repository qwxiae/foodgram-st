#!/bin/sh

python manage.py migrate
python manage.py load_data
python manage.py collectstatic --no-input
exec gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000