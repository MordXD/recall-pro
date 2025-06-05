# User Service

Микросервис для управления пользователями в проекте Recall Pro.

## Описание

Этот сервис отвечает за аутентификацию, авторизацию и управление пользователями системы.

## Технологии

- FastAPI
- Python-JOSE (JWT токены)
- Passlib (хеширование паролей)
- BCrypt
- Uvicorn

## Запуск

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
``` 