FROM python:3.11-slim

# Отключение буферизации для немедленного вывода логов
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Установка зависимостей отдельным слоем (кэширование)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY app/ ./app/

EXPOSE 8000

# Запуск ASGI-сервера uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
