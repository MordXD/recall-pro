.PHONY: help build up down restart logs shell db-shell clean test

# Цвета для вывода
GREEN=\033[0;32m
YELLOW=\033[1;33m
NC=\033[0m # No Color

help: ## Показать справку
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  ${GREEN}%-15s${NC} %s\n", $$1, $$2}'

build: ## Собрать все контейнеры
	@echo "${YELLOW}Сборка контейнеров...${NC}"
	docker-compose build

up: ## Запустить все сервисы
	@echo "${YELLOW}Запуск сервисов...${NC}"
	docker-compose up -d
	@echo "${GREEN}Сервисы запущены!${NC}"
	@echo "User Service: http://localhost:8001"
	@echo "Database Service: http://localhost:8002"
	@echo "PostgreSQL: localhost:5432"

down: ## Остановить все сервисы
	@echo "${YELLOW}Остановка сервисов...${NC}"
	docker-compose down
	@echo "${GREEN}Сервисы остановлены${NC}"

restart: ## Перезапустить все сервисы
	@echo "${YELLOW}Перезапуск сервисов...${NC}"
	docker-compose restart
	@echo "${GREEN}Сервисы перезапущены${NC}"

logs: ## Показать логи всех сервисов
	docker-compose logs -f

logs-user: ## Показать логи user-service
	docker-compose logs -f user-service

logs-db: ## Показать логи postgres
	docker-compose logs -f postgres

logs-db-service: ## Показать логи database-service
	docker-compose logs -f database-service

shell: ## Подключиться к контейнеру user-service
	docker-compose exec user-service /bin/bash

shell-db-service: ## Подключиться к контейнеру database-service
	docker-compose exec database-service /bin/bash

db-shell: ## Подключиться к PostgreSQL
	docker-compose exec postgres psql -U recall_user -d recall_pro

status: ## Показать статус контейнеров
	docker-compose ps

clean: ## Остановить и удалить все контейнеры и volumes
	@echo "${YELLOW}Очистка контейнеров и данных...${NC}"
	docker-compose down -v
	docker system prune -f
	@echo "${GREEN}Очистка завершена${NC}"

rebuild: ## Пересобрать и перезапустить
	@echo "${YELLOW}Пересборка и перезапуск...${NC}"
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d
	@echo "${GREEN}Пересборка завершена${NC}"

dev-stack: ## Запустить только PostgreSQL и database-service для разработки
	@echo "${YELLOW}Запуск PostgreSQL и Database Service для разработки...${NC}"
	docker-compose up -d postgres database-service
	@echo "${GREEN}PostgreSQL и Database Service запущены${NC}"

test-api: ## Тестировать API endpoints
	@echo "${YELLOW}Тестирование API...${NC}"
	@echo "Проверка User Service health endpoint:"
	curl -s http://localhost:8001/health | jq .
	@echo "\nПроверка Database Service health endpoint:"
	curl -s http://localhost:8002/health | jq .
	@echo "\nПроверка User Service root endpoint:"
	curl -s http://localhost:8001/ | jq .

test-db-api: ## Тестировать Database Service API
	@echo "${YELLOW}Тестирование Database Service API...${NC}"
	@echo "Получение пользователей:"
	curl -s http://localhost:8002/api/v1/users/ | jq .

install-deps: ## Установить зависимости для всех сервисов
	cd user-service && poetry install
	cd database-service && poetry install

run-user-local: ## Запустить user-service локально (нужен запущенный database-service)
	cd user-service && poetry run uvicorn src.main:app --reload --port 8000

run-db-local: ## Запустить database-service локально (нужна запущенная БД)
	cd database-service && poetry run uvicorn src.main:app --reload --port 8002

# Примеры использования API
signup-example: ## Пример регистрации пользователя
	@echo "${YELLOW}Регистрация тестового пользователя...${NC}"
	curl -X POST http://localhost:8001/api/v1/signup \
		-H "Content-Type: application/json" \
		-d '{"username": "testuser", "email": "test@example.com", "password": "password123"}' | jq .

login-example: ## Пример авторизации пользователя
	@echo "${YELLOW}Авторизация тестового пользователя...${NC}"
	curl -X POST http://localhost:8001/api/v1/login \
		-H "Content-Type: application/json" \
		-d '{"username": "testuser", "password": "password123"}' | jq . 