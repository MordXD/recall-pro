# Database Service

Микросервис для управления базой данных в проекте Recall Pro.

## Описание

Этот сервис предоставляет API для работы с базой данных, включая управление пользователями, колодами карточек и другими данными приложения.

## Технологии

- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic (для миграций)
- Uvicorn

## Запуск

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8002 --reload
``` 