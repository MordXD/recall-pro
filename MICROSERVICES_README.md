# Recall Pro - Микросервисная архитектура

## Описание архитектуры

Это микросервисная архитектура для приложения Recall Pro с разделением на отдельные сервисы:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Service  │────│ Database Service│────│   PostgreSQL    │
│     :8001       │    │      :8002      │    │     :5432       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Сервисы

### 1. **PostgreSQL** (порт 5432)
- Основная база данных
- Хранит все данные приложения
- Доступна только для Database Service

### 2. **Database Service** (порт 8002)
- Микросервис для работы с базой данных
- Предоставляет REST API для CRUD операций
- Единственная точка доступа к PostgreSQL
- Управляет пользователями и токенами

### 3. **User Service** (порт 8001)
- Сервис аутентификации и авторизации
- Работает с Database Service через HTTP API
- Обрабатывает JWT токены
- Хеширует пароли

### 4. **API Gateway** (планируется)
- Единая точка входа для клиентов
- Маршрутизация запросов к сервисам
- Аутентификация и авторизация

### 5. **Deck Service** (планируется)
- Управление колодами карточек
- Работает с Database Service через HTTP API

## Быстрый запуск

1. Скопируйте переменные окружения:
```bash
cp env.example .env
```

2. Запустите все сервисы:
```bash
make up
# или
docker-compose up -d
```

3. Проверьте работу:
```bash
make test-api
```

## API Endpoints

### User Service (http://localhost:8001)

#### Аутентификация
- `POST /api/v1/signup` - Регистрация пользователя
- `POST /api/v1/login` - Авторизация пользователя
- `POST /api/v1/logout` - Выход из системы
- `POST /api/v1/refresh` - Обновление access токена
- `GET /api/v1/verify` - Проверка валидности токена

#### Служебные
- `GET /` - Информация о сервисе
- `GET /health` - Проверка состояния сервиса

### Database Service (http://localhost:8002)

#### Пользователи
- `POST /api/v1/users/` - Создать пользователя
- `GET /api/v1/users/{user_id}` - Получить пользователя по ID
- `GET /api/v1/users/search/by-username/{username}` - Поиск по имени
- `GET /api/v1/users/search/by-email/{email}` - Поиск по email
- `GET /api/v1/users/` - Список пользователей с пагинацией
- `PUT /api/v1/users/{user_id}` - Обновить пользователя
- `DELETE /api/v1/users/{user_id}` - Удалить пользователя

#### Токены
- `POST /api/v1/tokens/` - Создать refresh токен
- `GET /api/v1/tokens/verify/{token_hash}` - Проверить токен
- `GET /api/v1/tokens/user/{user_id}` - Токены пользователя
- `POST /api/v1/tokens/revoke` - Отозвать токен
- `POST /api/v1/tokens/revoke-user/{user_id}` - Отозвать все токены пользователя
- `POST /api/v1/tokens/cleanup` - Очистить просроченные токены

#### Служебные
- `GET /` - Информация о сервисе
- `GET /health` - Проверка состояния сервиса

## Примеры использования

### Регистрация пользователя
```bash
curl -X POST http://localhost:8001/api/v1/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "user@example.com",
    "password": "securepassword"
  }'
```

### Авторизация
```bash
curl -X POST http://localhost:8001/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "password": "securepassword"
  }'
```

### Работа с Database Service
```bash
# Получить всех пользователей
curl http://localhost:8002/api/v1/users/

# Получить пользователя по ID
curl http://localhost:8002/api/v1/users/1

# Поиск пользователя по имени
curl http://localhost:8002/api/v1/users/search/by-username/newuser
```

## Развертывание

### Для разработки

1. Запустить только базу данных и Database Service:
```bash
make dev-stack
```

2. Запустить User Service локально:
```bash
make run-user-local
```

### Для продакшена

1. Измените переменные окружения в `.env`
2. Соберите образы:
```bash
make build
```
3. Запустите:
```bash
make up
```

## Команды Makefile

```bash
make help              # Показать все команды
make up                # Запустить все сервисы
make down              # Остановить сервисы
make logs              # Показать логи всех сервисов
make logs-user         # Логи User Service
make logs-db-service   # Логи Database Service
make test-api          # Тестировать API
make dev-stack         # Запустить PostgreSQL + Database Service
make clean             # Очистить все данные
```

## Мониторинг и логирование

### Проверка состояния сервисов
```bash
make status
```

### Просмотр логов
```bash
# Все сервисы
make logs

# Отдельные сервисы
make logs-user
make logs-db-service
make logs-db
```

### Health checks
```bash
# User Service
curl http://localhost:8001/health

# Database Service
curl http://localhost:8002/health
```

## Архитектурные преимущества

### Разделение ответственности
- **User Service**: Только аутентификация и бизнес-логика
- **Database Service**: Только работа с данными
- **PostgreSQL**: Только хранение данных

### Масштабируемость
- Каждый сервис можно масштабировать независимо
- Горизонтальное масштабирование Database Service
- Возможность добавления кеша между сервисами

### Безопасность
- База данных изолирована от внешнего доступа
- Токены хешируются перед сохранением
- Централизованное управление доступом к данным

### Тестируемость
- Каждый сервис тестируется независимо
- Возможность мокирования Database Service
- Изолированное тестирование бизнес-логики

## Troubleshooting

### Database Service недоступен
```bash
# Проверить статус
make status

# Посмотреть логи
make logs-db-service

# Перезапустить
docker-compose restart database-service
```

### Ошибки подключения к PostgreSQL
```bash
# Проверить PostgreSQL
make logs-db
docker-compose exec postgres pg_isready -U recall_user

# Подключиться к базе
make db-shell
```

### User Service не может подключиться к Database Service
```bash
# Проверить переменные окружения
docker-compose exec user-service env | grep DATABASE_SERVICE_URL

# Проверить сеть
docker network ls
docker network inspect recall_pro_recall_pro_network
``` 