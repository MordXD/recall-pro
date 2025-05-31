# Recall Pro - Docker Setup

## Описание

Это микросервисная архитектура для приложения Recall Pro с использованием Docker Compose.

## Сервисы

- **PostgreSQL** - База данных
- **User Service** - Сервис аутентификации и управления пользователями
- **API Gateway** - (планируется)
- **Deck Service** - (планируется)

## Требования

- Docker
- Docker Compose

## Быстрый запуск

1. Клонируйте репозиторий
2. Скопируйте файл с переменными окружения:
```bash
cp env.example .env
```

3. Отредактируйте `.env` файл при необходимости

4. Запустите сервисы:
```bash
docker-compose up -d
```

5. Проверьте работу сервисов:
```bash
# Проверка PostgreSQL
docker-compose ps

# Проверка User Service
curl http://localhost:8001/health
```

## API Endpoints

### User Service (порт 8001)

- `GET /` - Корневой эндпоинт
- `GET /health` - Проверка здоровья сервиса
- `POST /api/v1/signup` - Регистрация пользователя
- `POST /api/v1/login` - Авторизация пользователя
- `POST /api/v1/logout` - Выход из системы
- `POST /api/v1/refresh` - Обновление токена

### Примеры запросов

#### Регистрация
```bash
curl -X POST http://localhost:8001/api/v1/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
```

#### Авторизация
```bash
curl -X POST http://localhost:8001/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

## База данных

### Подключение к PostgreSQL

```bash
# Подключение через psql
docker exec -it recall_pro_postgres psql -U recall_user -d recall_pro

# Или через внешнее подключение
psql -h localhost -p 5432 -U recall_user -d recall_pro
```

### Просмотр таблиц

```sql
-- Просмотр всех таблиц
\dt

-- Просмотр пользователей
SELECT * FROM users;

-- Просмотр refresh токенов
SELECT * FROM refresh_tokens;
```

## Управление контейнерами

```bash
# Запуск в фоновом режиме
docker-compose up -d

# Просмотр логов
docker-compose logs -f user-service
docker-compose logs -f postgres

# Остановка сервисов
docker-compose down

# Остановка с удалением volumes (ОСТОРОЖНО: удалит данные)
docker-compose down -v

# Пересборка контейнеров
docker-compose build --no-cache

# Перезапуск конкретного сервиса
docker-compose restart user-service
```

## Разработка

Для разработки рекомендуется:

1. Запустить только PostgreSQL через Docker:
```bash
docker-compose up -d postgres
```

2. Запустить User Service локально:
```bash
cd user-service
poetry install
poetry run uvicorn src.main:app --reload --port 8000
```

## Переменные окружения

Основные переменные окружения описаны в файле `env.example`:

- `DATABASE_URL` - URL подключения к базе данных
- `SECRET_KEY` - Секретный ключ для JWT токенов
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Время жизни access токена (минуты)
- `REFRESH_TOKEN_EXPIRE_DAYS` - Время жизни refresh токена (дни)

## Безопасность

⚠️ **ВАЖНО**: В продакшене обязательно:

1. Измените `SECRET_KEY` на длинный случайный ключ
2. Измените пароли базы данных
3. Настройте CORS для конкретных доменов
4. Используйте HTTPS
5. Настройте файрвол

## Troubleshooting

### База данных не запускается

1. Проверьте, что порт 5432 свободен:
```bash
sudo netstat -tlnp | grep 5432
```

2. Проверьте логи PostgreSQL:
```bash
docker-compose logs postgres
```

### User Service не может подключиться к базе данных

1. Проверьте, что PostgreSQL запущен и здоров:
```bash
docker-compose ps postgres
```

2. Проверьте переменные окружения в docker-compose.yml

3. Проверьте логи сервиса:
```bash
docker-compose logs user-service
``` 