FROM python:3.12-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
RUN pip install poetry

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы Poetry
COPY pyproject.toml ./

# Настраиваем Poetry чтобы не создавать виртуальную среду
RUN poetry config virtualenvs.create false

# Устанавливаем зависимости
RUN poetry install --without dev

# Копируем исходный код
COPY src/ ./src/

# Открываем порт
EXPOSE 8002

# Запускаем приложение
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8002", "--reload"] 