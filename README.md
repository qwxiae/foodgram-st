## Настройте проект
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