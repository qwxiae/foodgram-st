- Клонируйте репозиторий с проектом на свой компьютер.
```
git clone https://github.com/clmr-y/foodgram-st.git
```
- Установить и активировать виртуальное окружение

```
source /venv/bin/activate
```

- Установить зависимости из файла requirements.txt

```
python -m pip install --upgrade pip
```
```
pip install -r requirements.txt
```
- Создать файл .env в папке проектов backend и infra:
```.env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
DEBUG=0
```

### Выполните миграции:
```
python manage.py migrate
```

- В папке с файлом manage.py выполнить команду:
```
python manage.py runserver
```

- Создание супер пользователя 
```
python manage.py createsuperuser
```

### Загрузите статику:
```
python manage.py collectstatic --no-input
```
### Заполните базу тестовыми данными: 
```
python manage.py data_loads
```

## Запуск проекта через Docker

Выполните команду:
```
cd ../infra
docker-compose up -d --build
```

### Создайте суперпользователя:
```
docker-compose exec backend python manage.py createsuperuser
```

### Загрузите статику:
```
docker-compose exec backend python manage.py collectstatic --no-input
```

### Заполните базу тестовыми данными:
```
docker-compose exec backend python manage.py dataloads
```
