FROM python:3.12-slim

WORKDIR /app

# Копируем файлы зависимостей
COPY poetry.lock pyproject.toml requirements.txt ./

# Обновляем pip и ставим зависимости
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Копируем весь остальной код проекта
COPY . .

# Запуск: миграции, статика, сервер
CMD ["sh", "-c", "python manage.py collectstatic --noinput && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
