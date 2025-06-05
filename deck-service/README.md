# Deck Service - Управление колодами карточек

## Описание

Deck Service — это микросервис для управления колодами карточек в приложении Recall Pro. Он отвечает за создание, редактирование, удаление колод и карточек, а также за импорт/экспорт данных. **Все карточки поддерживают Markdown формат** с изображениями, таблицами, списками и другими элементами форматирования.

## Архитектура

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Gateway   │────│   Deck Service  │────│ Database Service│
│     :8000       │    │      :8003      │    │      :8002      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                               │
                                               ▼
                                       ┌─────────────────┐
                                       │   PostgreSQL    │
                                       │     :5432       │
                                       └─────────────────┘
```

## Основные функции

### 1. **Управление колодами**
- ✅ Создание новых колод
- ✅ Редактирование метаданных колоды
- ✅ Удаление колод
- ✅ Получение списка колод пользователя
- ✅ Публичные/приватные колоды

### 2. **Управление карточками**
- ✅ Добавление карточек в колоду
- ✅ Редактирование вопросов и ответов
- ✅ Удаление карточек
- ✅ Поддержка изображений в карточках
- ✅ Массовые операции с карточками

### 3. **Импорт/Экспорт**
- ✅ Импорт из CSV файлов
- ✅ Импорт из JSON файлов
- ✅ Экспорт в CSV/JSON форматы
- ✅ Шаблоны для импорта

### 4. **Теги и категории**
- ✅ Добавление тегов к колодам
- ✅ Категоризация колод
- ✅ Поиск по тегам
- ✅ Автодополнение тегов

## Модель данных

### Колода (Deck)
```python
class Deck:
    id: UUID
    owner_id: UUID
    title: str
    description: Optional[str]
    is_public: bool = False
    tags: List[str] = []
    category: Optional[str]
    created_at: datetime
    updated_at: datetime
    cards_count: int = 0
```

### Карточка (Card)
```python
class Card:
    id: UUID
    deck_id: UUID
    question: str  # Markdown контент
    answer: str    # Markdown контент
    question_html: str  # Преобразованный HTML (кешируется)
    answer_html: str    # Преобразованный HTML (кешируется)
    attachments: List[str] = []  # URL изображений и файлов
    position: int  # Порядок в колоде
    created_at: datetime
    updated_at: datetime
```

### Категория (Category)
```python
class Category:
    id: UUID
    name: str
    description: Optional[str]
    color: str  # HEX цвет для UI
```

## API Endpoints

### Управление колодами

#### `GET /api/v1/decks/`
Получить список колод пользователя с пагинацией

**Query параметры:**
- `page: int = 1` - Номер страницы
- `size: int = 20` - Размер страницы
- `category: str` - Фильтр по категории
- `tags: List[str]` - Фильтр по тегам
- `search: str` - Поиск по названию и описанию

**Ответ:**
```json
{
  "items": [
    {
      "id": "uuid",
      "title": "English Vocabulary",
      "description": "Basic English words",
      "is_public": false,
      "tags": ["english", "vocabulary"],
      "category": "Languages",
      "cards_count": 150,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-02T00:00:00Z"
    }
  ],
  "total": 5,
  "page": 1,
  "size": 20,
  "pages": 1
}
```

#### `POST /api/v1/decks/`
Создать новую колоду

**Тело запроса:**
```json
{
  "title": "My New Deck",
  "description": "Description of my deck",
  "is_public": false,
  "tags": ["tag1", "tag2"],
  "category": "Science"
}
```

#### `GET /api/v1/decks/{deck_id}`
Получить колоду по ID

#### `PUT /api/v1/decks/{deck_id}`
Обновить колоду

#### `DELETE /api/v1/decks/{deck_id}`
Удалить колоду (со всеми карточками)

### Управление карточками

#### `GET /api/v1/decks/{deck_id}/cards/`
Получить карточки колоды

**Query параметры:**
- `page: int = 1`
- `size: int = 50`

#### `POST /api/v1/decks/{deck_id}/cards/`
Добавить карточку в колоду

**Тело запроса:**
```json
{
  "question": "## Что такое Python?\n\nPython - это:\n- Высокоуровневый язык программирования\n- Интерпретируемый\n- Объектно-ориентированный\n\n![Python Logo](https://python.org/static/img/python-logo.png)",
  "answer": "**Python** — это *мощный* язык программирования, который:\n\n1. **Прост в изучении** благодаря читаемому синтаксису\n2. **Универсален** — подходит для:\n   - Web-разработки\n   - Data Science\n   - Machine Learning\n   - Автоматизации\n\n```python\n# Пример кода\nprint('Hello, World!')\n```\n\n> Python был создан Гвидо ван Россумом в 1991 году"
}
```

#### `PUT /api/v1/cards/{card_id}`
Обновить карточку

#### `DELETE /api/v1/cards/{card_id}`
Удалить карточку

#### `POST /api/v1/decks/{deck_id}/cards/bulk`
Массовое добавление карточек

**Тело запроса:**
```json
{
  "cards": [
    {
      "question": "# JavaScript\n\n## Что это?\nЯзык программирования для веб-разработки\n\n![JS](https://example.com/js.png)",
      "answer": "**JavaScript** — это:\n\n- Язык для фронтенда и бэкенда\n- Динамически типизированный\n- Поддерживает ООП и функциональное программирование\n\n```javascript\nconsole.log('Hello, JS!');\n```"
    },
    {
      "question": "## HTML структура\n\n```html\n<!DOCTYPE html>\n<html>\n  <head>\n    <title>Page</title>\n  </head>\n</html>\n```",
      "answer": "Это базовая **HTML структура**:\n\n| Элемент | Описание |\n|---------|----------|\n| `<!DOCTYPE html>` | Объявление типа документа |\n| `<html>` | Корневой элемент |\n| `<head>` | Метаданные страницы |\n| `<title>` | Заголовок страницы |"
    }
  ]
}
```

### Импорт/Экспорт

#### `POST /api/v1/decks/{deck_id}/import/csv`
Импортировать карточки из CSV файла

**Формат CSV с Markdown:**
```csv
question,answer
"# Что такое Git?\n\nСистема контроля версий","**Git** — это распределенная система контроля версий\n\n```bash\ngit init\ngit add .\ngit commit -m ""Initial commit""\n```"
"## Docker основы\n\n![Docker](https://example.com/docker.png)","**Docker** контейнеризирует приложения:\n\n- Изоляция\n- Портативность\n- Масштабируемость"
```

**Тело запроса:** `multipart/form-data`
- `file: File` - CSV файл с Markdown контентом
- `has_header: bool = true` - Есть ли заголовки в файле
- `question_column: int = 0` - Номер колонки с вопросами (Markdown)
- `answer_column: int = 1` - Номер колонки с ответами (Markdown)
- `render_html: bool = true` - Преобразовать Markdown в HTML сразу

#### `GET /api/v1/decks/{deck_id}/export/csv`
Экспортировать колоду в CSV с Markdown контентом

#### `GET /api/v1/decks/{deck_id}/export/json`
Экспортировать колоду в JSON

**Пример экспорта:**
```json
{
  "deck": {
    "id": "uuid",
    "title": "Programming Basics",
    "description": "Basic programming concepts",
    "cards": [
      {
        "question": "# Python\n\n## Особенности\n- Простой синтаксис\n- Большое сообщество",
        "answer": "**Python** — отличный выбор для начинающих\n\n```python\nprint('Hello')\n```",
        "question_html": "<h1>Python</h1><h2>Особенности</h2><ul><li>Простой синтаксис</li><li>Большое сообщество</li></ul>",
        "answer_html": "<p><strong>Python</strong> — отличный выбор для начинающих</p><pre><code class=\"language-python\">print('Hello')\n</code></pre>",
        "attachments": ["https://example.com/python-logo.png"]
      }
    ]
  }
}
```

### Категории и теги

#### `GET /api/v1/categories/`
Получить список всех категорий

#### `GET /api/v1/tags/search`
Поиск тегов с автодополнением

**Query параметры:**
- `q: str` - Поисковый запрос
- `limit: int = 10` - Лимит результатов

### Публичные колоды

#### `GET /api/v1/public/decks/`
Получить список публичных колод

#### `POST /api/v1/public/decks/{deck_id}/clone`
Клонировать публичную колоду себе

## Взаимодействие с Database Service

Deck Service взаимодействует с Database Service через HTTP API для всех операций с базой данных. **Особое внимание уделяется обработке Markdown контента.**

### Примеры взаимодействия

#### Создание колоды
```python
# deck-service/services/deck_service.py
import httpx
from typing import Dict, Any

class DeckService:
    def __init__(self, database_service_url: str):
        self.db_url = database_service_url
        self.client = httpx.AsyncClient()
    
    async def create_deck(self, deck_data: Dict[str, Any]) -> Dict[str, Any]:
        response = await self.client.post(
            f"{self.db_url}/api/v1/decks/",
            json=deck_data
        )
        response.raise_for_status()
        return response.json()
    
    async def get_user_decks(self, user_id: str, page: int = 1, size: int = 20):
        response = await self.client.get(
            f"{self.db_url}/api/v1/decks/user/{user_id}",
            params={"page": page, "size": size}
        )
        response.raise_for_status()
        return response.json()
```

#### Создание карточки с Markdown
```python
# deck-service/services/card_service.py
import httpx
import markdown
from markdown.extensions import codehilite, tables, fenced_code
from typing import Dict, Any, List
import re

class CardService:
    def __init__(self, database_service_url: str):
        self.db_url = database_service_url
        self.client = httpx.AsyncClient()
        
        # Настройка Markdown процессора
        self.md_processor = markdown.Markdown(
            extensions=[
                'codehilite',
                'tables', 
                'fenced_code',
                'toc',
                'attr_list'
            ],
            extension_configs={
                'codehilite': {
                    'css_class': 'highlight',
                    'use_pygments': True
                }
            }
        )
    
    async def create_card(self, deck_id: str, card_data: Dict[str, Any]) -> Dict[str, Any]:
        # Валидация Markdown контента
        question_md = card_data['question']
        answer_md = card_data['answer']
        
        # Извлекаем изображения из Markdown
        attachments = self._extract_images_from_markdown(question_md, answer_md)
        
        # Конвертируем Markdown в HTML для кеширования
        question_html = self.md_processor.convert(question_md)
        answer_html = self.md_processor.convert(answer_md)
        
        # Подготавливаем данные для Database Service
        db_card_data = {
            **card_data,
            'deck_id': deck_id,
            'question_html': question_html,
            'answer_html': answer_html,
            'attachments': attachments
        }
        
        # Отправляем в Database Service
        response = await self.client.post(
            f"{self.db_url}/api/v1/cards/",
            json=db_card_data
        )
        response.raise_for_status()
        return response.json()
    
    def _extract_images_from_markdown(self, question: str, answer: str) -> List[str]:
        """Извлекает URL изображений из Markdown контента"""
        image_pattern = r'!\[.*?\]\((.*?)\)'
        images = []
        
        # Поиск изображений в вопросе и ответе
        images.extend(re.findall(image_pattern, question))
        images.extend(re.findall(image_pattern, answer))
        
        return list(set(images))  # Убираем дубликаты
    
    async def render_card_html(self, card_data: Dict[str, Any]) -> Dict[str, Any]:
        """Перерендерить HTML для карточки"""
        question_html = self.md_processor.convert(card_data['question'])
        answer_html = self.md_processor.convert(card_data['answer'])
        
        return {
            **card_data,
            'question_html': question_html,
            'answer_html': answer_html
        }
```

#### Импорт CSV с Markdown контентом
```python
# deck-service/services/import_service.py
import csv
import io
from typing import List, Dict, Any

class ImportService:
    def __init__(self, card_service: CardService):
        self.card_service = card_service
    
    async def import_csv_with_markdown(
        self, 
        deck_id: str, 
        file_content: bytes,
        has_header: bool = True,
        question_column: int = 0,
        answer_column: int = 1
    ) -> Dict[str, Any]:
        
        # Декодируем файл
        content = file_content.decode('utf-8')
        csv_reader = csv.reader(io.StringIO(content))
        
        if has_header:
            next(csv_reader)  # Пропускаем заголовок
        
        imported_cards = []
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=1):
            try:
                if len(row) <= max(question_column, answer_column):
                    errors.append(f"Row {row_num}: insufficient columns")
                    continue
                
                question_md = row[question_column].strip()
                answer_md = row[answer_column].strip()
                
                if not question_md or not answer_md:
                    errors.append(f"Row {row_num}: empty question or answer")
                    continue
                
                # Создаем карточку с Markdown контентом
                card = await self.card_service.create_card(deck_id, {
                    'question': question_md,
                    'answer': answer_md
                })
                
                imported_cards.append(card)
                
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
        return {
            'imported_count': len(imported_cards),
            'error_count': len(errors),
            'errors': errors,
            'cards': imported_cards
        }
```

## Структура проекта

```
deck-service/
├── src/
│   ├── __init__.py
│   ├── main.py                 # FastAPI приложение
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── __main__.py
│   ├── models/                 # Pydantic модели
│   │   ├── __init__.py
│   │   ├── deck.py
│   │   ├── card.py            # Модели с поддержкой Markdown
│   │   └── category.py
│   ├── services/               # Бизнес-логика
│   │   ├── __init__.py
│   │   ├── deck_service.py
│   │   ├── card_service.py    # Обработка Markdown
│   │   ├── markdown_service.py # Рендеринг Markdown
│   │   ├── import_service.py  # Импорт с Markdown
│   │   └── export_service.py  # Экспорт с Markdown
│   ├── api/                    # API роутеры
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── decks.py
│   │   │   ├── cards.py       # API для Markdown карточек
│   │   │   ├── import_export.py
│   │   │   └── categories.py
│   ├── utils/                  # Утилиты
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── files.py
│   │   ├── markdown_utils.py  # Утилиты для Markdown
│   │   └── validation.py      # Валидация Markdown
│   └── config.py               # Настройки
├── tests/                      # Тесты
│   ├── __init__.py
│   ├── test_decks.py
│   ├── test_cards.py
│   ├── test_markdown.py       # Тесты Markdown функций
│   └── test_import_export.py
├── requirements.txt            # Включает markdown, pygments
├── Dockerfile
└── README.md
```

## Переменные окружения

```bash
# Database Service
DATABASE_SERVICE_URL=http://database-service:8002

# App settings
PORT=8003
DEBUG=true
ENVIRONMENT=development

# File upload settings
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_FILE_TYPES=csv,json,txt,md

# Markdown settings
MARKDOWN_SAFE_MODE=True  # Безопасный режим Markdown
ALLOW_HTML_IN_MARKDOWN=False  # Разрешить HTML в Markdown
MAX_MARKDOWN_SIZE=50000  # Максимальный размер Markdown контента

# Import/Export settings
MAX_CARDS_PER_IMPORT=1000
EXPORT_RATE_LIMIT=10  # requests per minute
```

## Запуск сервиса

### С Docker Compose (рекомендуется)

1. Добавьте в `docker-compose.yml`:
```yaml
deck-service:
  build: 
    context: ./deck-service
    dockerfile: Dockerfile
  container_name: recall_pro_deck_service
  environment:
    DATABASE_SERVICE_URL: http://database-service:8002
    PORT: 8003
    DEBUG: true
    ENVIRONMENT: development
  ports:
    - "8003:8003"
  depends_on:
    - database-service
  networks:
    - recall_pro_network
  volumes:
    - ./deck-service/src:/app/src
  restart: unless-stopped
```

2. Запустите:
```bash
docker-compose up deck-service
```

### Локальная разработка

```bash
cd deck-service
pip install -r requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port 8003 --reload
```

## Примеры использования

### Создание колоды
```bash
curl -X POST http://localhost:8003/api/v1/decks/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "title": "Python Basics",
    "description": "Basic Python concepts",
    "tags": ["python", "programming"],
    "category": "Programming"
  }'
```

### Добавление карточки с Markdown
```bash
curl -X POST http://localhost:8003/api/v1/decks/DECK_ID/cards/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "question": "# Python Lists\n\n## Что это?\nЗащищенный список элементов:\n\n```python\nmy_list = [1, 2, 3]\n```\n\n![List diagram](https://example.com/list.png)",
    "answer": "**Python List** — это упорядоченная коллекция:\n\n| Метод | Описание |\n|-------|----------|\n| `append()` | Добавить элемент |\n| `remove()` | Удалить элемент |\n| `pop()` | Извлечь элемент |\n\n> Lists are mutable in Python!"
  }'
```

### Импорт Markdown карточек из CSV
```bash
curl -X POST http://localhost:8003/api/v1/decks/DECK_ID/import/csv \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@cards_with_markdown.csv" \
  -F "has_header=true" \
  -F "render_html=true"
```

### Получение карточки с HTML версией
```bash
curl -X GET http://localhost:8003/api/v1/cards/CARD_ID?include_html=true \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Ответ:**
```json
{
  "id": "uuid",
  "question": "# JavaScript\n\n## Что это?\n```js\nconsole.log('Hello');\n```",
  "answer": "**JavaScript** — язык программирования",
  "question_html": "<h1>JavaScript</h1><h2>Что это?</h2><pre><code class=\"language-js\">console.log('Hello');\n</code></pre>",
  "answer_html": "<p><strong>JavaScript</strong> — язык программирования</p>",
  "attachments": [],
  "created_at": "2024-01-01T00:00:00Z"
}
```

## Тестирование

### Запуск тестов
```bash
# Все тесты
pytest

# С покрытием
pytest --cov=src

# Конкретный файл
pytest tests/test_decks.py
```

### Тестирование Markdown функций
```python
# tests/test_markdown.py
import pytest
from src.services.markdown_service import MarkdownService

def test_markdown_to_html():
    md_service = MarkdownService()
    
    markdown_text = "# Header\n\n**Bold text** and `code`"
    html = md_service.convert_to_html(markdown_text)
    
    assert "<h1>Header</h1>" in html
    assert "<strong>Bold text</strong>" in html
    assert "<code>code</code>" in html

def test_image_extraction():
    md_service = MarkdownService()
    
    markdown_text = "![Alt text](https://example.com/image.png) and ![Another](https://test.com/img.jpg)"
    images = md_service.extract_images(markdown_text)
    
    assert len(images) == 2
    assert "https://example.com/image.png" in images
    assert "https://test.com/img.jpg" in images

def test_code_highlighting():
    md_service = MarkdownService()
    
    markdown_text = "```python\nprint('Hello')\n```"
    html = md_service.convert_to_html(markdown_text)
    
    assert "highlight" in html
    assert "language-python" in html
```

## Мониторинг и логирование

### Health Check
```bash
curl http://localhost:8003/health
```

### Метрики
- Количество колод по пользователям
- Количество карточек в колодах
- Статистика импорта/экспорта
- Время отклика API
- **Статистика Markdown рендеринга**
- **Размер Markdown контента**
- **Использование изображений в карточках**

### Логирование
```python
import logging

logger = logging.getLogger(__name__)

# Примеры логов
logger.info(f"Deck created: {deck_id} by user {user_id}")
logger.info(f"Markdown rendered: {len(question_md)} chars -> {len(question_html)} chars")
logger.warning(f"Large markdown content: {content_size} bytes in card {card_id}")
logger.warning(f"Invalid image URL detected: {img_url} in card {card_id}")
logger.error(f"Markdown rendering failed: {error}")
```

## Производительность

### Кеширование
- Кеш часто используемых колод в Redis
- **Кеш рендеренного HTML контента** 
- Кеш метаданных категорий и тегов
- Кеш результатов поиска
- **Кеш извлеченных изображений**

### Оптимизации базы данных
- Индексы на owner_id, category, tags
- Пагинация для больших списков
- Ленивая загрузка карточек
- **Индексы для полнотекстового поиска по Markdown**

### Ограничения
- Максимум 1000 карточек в колоде
- **Максимум 50KB для Markdown контента карточки**
- Максимум 10MB для импортируемых файлов
- Rate limiting для экспорта (10 запросов/минута)
- **Максимум 10 изображений на карточку**

## Безопасность

### Аутентификация
- JWT токены от User Service
- Проверка прав доступа к колодам
- Валидация данных с помощью Pydantic

### Файловая безопасность
- Проверка типов загружаемых файлов
- Ограничение размера файлов
- Сканирование CSV на вредоносный контент

### Безопасность Markdown
- **Санитизация HTML вывода**
- **Блокировка опасных HTML тегов**
- **Валидация URL изображений**
- **Ограничение размера Markdown контента**
- **Защита от XSS через Markdown**

## Интеграции

### С User Service
- Проверка JWT токенов
- Получение информации о пользователе
- Проверка прав доступа

### С Search Service (будущее)
- Индексация колод для поиска
- **Полнотекстовый поиск по Markdown контенту**
- Обновление поискового индекса при изменениях

### С Study Service (будущее)  
- Предоставление карточек для изучения
- **Рендеринг Markdown для учебных режимов**
- Статистика использования колод

### С File Storage Service (будущее)
- **Загрузка изображений для карточек**
- **Оптимизация изображений**
- **CDN для быстрой загрузки контента**

## TODO и планы развития

### Ближайшие задачи
- [x] Реализация базового CRUD для колод
- [x] **Поддержка Markdown в карточках**
- [x] **Рендеринг HTML из Markdown**
- [ ] Импорт/экспорт CSV с Markdown
- [ ] Система тегов
- [ ] Публичные колоды

### Будущие функции
- [ ] **Встроенный редактор Markdown**
- [ ] **Предпросмотр Markdown в реальном времени**
- [ ] **Поддержка LaTeX формул**
- [ ] **Поддержка mermaid диаграмм**
- [ ] Совместная работа над колодами
- [ ] Версионирование колод
- [ ] API для мобильных приложений
- [ ] Интеграция с внешними сервисами (Anki, Quizlet)
- [ ] **Автоматическое извлечение изображений из веб-страниц**

### Расширенные Markdown функции
- [ ] **Поддержка математических формул** (MathJax/KaTeX)
- [ ] **Интерактивные элементы** (чекбоксы, формы)
- [ ] **Встраивание видео** (YouTube, Vimeo)
- [ ] **Поддержка аудио файлов**
- [ ] **Диаграммы и схемы** (Mermaid, PlantUML)

## Примеры карточек с Markdown

### Карточка по программированию
```markdown
# Python Functions

## Синтаксис
```python
def function_name(parameters):
    """Docstring"""
    # Function body
    return value
```

## Типы параметров
| Тип | Синтаксис | Пример |
|-----|-----------|--------|
| Обязательный | `def func(param):` | `func(5)` |
| По умолчанию | `def func(param=default):` | `func()` |
| *args | `def func(*args):` | `func(1, 2, 3)` |
| **kwargs | `def func(**kwargs):` | `func(a=1, b=2)` |

> **Совет:** Всегда используйте docstrings для документирования функций!

![Python Functions](https://example.com/python-functions.png)
```

### Карточка по истории
```markdown
# Великая французская революция

## Даты
**1789-1799 гг.**

## Основные события
1. **1789** — Созыв Генеральных штатов
2. **14 июля 1789** — Взятие Бастилии  
3. **1792** — Провозглашение республики
4. **1799** — Переворот Наполеона

## Последствия
- Конец абсолютной монархии
- Декларация прав человека и гражданина
- Влияние на всю Европу

> *"Свобода, равенство, братство!"* — девиз революции

![Взятие Бастилии](https://example.com/bastille.jpg)
```

### Карточка по математике
```markdown
# Теорема Пифагора

## Формула
```
a² + b² = c²
```

Где:
- **a, b** — катеты прямоугольного треугольника
- **c** — гипотенуза

## Доказательство
Существует более **400 способов** доказательства!

### Геометрическое доказательство
1. Построим квадрат со стороной (a + b)
2. Площадь = (a + b)²
3. Разложим на части...

![Доказательство Пифагора](https://example.com/pythagoras-proof.png)

> **Применение:** Расчет расстояний, строительство, навигация
```

## Особенности работы с Markdown

### Поддерживаемые элементы
- ✅ **Заголовки** (`# ## ###`)
- ✅ **Форматирование** (`**bold**`, `*italic*`, `~~strikethrough~~`)
- ✅ **Списки** (нумерованные и маркированные)
- ✅ **Таблицы** с поддержкой выравнивания
- ✅ **Код** (инлайн и блоки с подсветкой синтаксиса)
- ✅ **Изображения** с автоматическим извлечением URL
- ✅ **Ссылки** с валидацией
- ✅ **Цитаты** (`> quote`)
- ✅ **Горизонтальные линии** (`---`)

### Безопасность Markdown
```python
# src/utils/markdown_utils.py
import bleach
from markdown import markdown

ALLOWED_TAGS = [
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'p', 'br', 'strong', 'em', 'u', 's',
    'ul', 'ol', 'li', 'blockquote',
    'code', 'pre', 'table', 'thead', 'tbody', 'tr', 'td', 'th',
    'img', 'a'
]

ALLOWED_ATTRIBUTES = {
    'img': ['src', 'alt', 'title'],
    'a': ['href', 'title'],
    'code': ['class'],
    'pre': ['class']
}

def sanitize_markdown_html(html: str) -> str:
    """Очистка HTML от потенциально опасного контента"""
    return bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )
```

### Валидация изображений
```python
def validate_image_urls(markdown_content: str) -> List[str]:
    """Валидация URL изображений в Markdown"""
    images = extract_images_from_markdown(markdown_content)
    invalid_urls = []
    
    for img_url in images:
        if not img_url.startswith(('http://', 'https://')):
            invalid_urls.append(img_url)
        elif not img_url.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
            invalid_urls.append(img_url)
    
    return invalid_urls
```

### Подсветка синтаксиса
Поддерживаемые языки программирования:
- Python, JavaScript, TypeScript
- HTML, CSS, SQL
- Java, C++, C#, Go, Rust
- Bash, PowerShell
- JSON, YAML, XML

**Пример использования:**
```markdown
```python
def hello_world():
    print("Hello, World!")
    return True
```
```

### Шаблоны для быстрого создания карточек

#### Шаблон "Программирование"
```markdown
# [Название концепции]

## Что это?
[Краткое описание]

## Синтаксис
```[язык]
[код примера]
```

## Применение
- [Пример использования 1]
- [Пример использования 2]

![Диаграмма](URL_изображения)
```

#### Шаблон "Языки"
```markdown
# [Слово/Фраза]

**Перевод:** [перевод]

## Примеры
1. **[Предложение на языке]** — [перевод]
2. **[Предложение на языке]** — [перевод]

> **Заметка:** [дополнительная информация]
```

#### Шаблон "Наука"
```markdown
# [Термин/Формула]

## Определение
[Определение понятия]

## Формула
```
[математическая формула]
```

| Обозначение | Описание |
|-------------|----------|
| [символ]    | [описание] |

![Схема](URL_изображения)
```

## Поддержка

Для вопросов и багрепортов используйте Issues в GitHub репозитории проекта.

### FAQ по Markdown

**Q: Какие изображения поддерживаются?**  
A: PNG, JPG, JPEG, GIF, WebP с максимальным размером 5MB каждое.

**Q: Можно ли использовать HTML в Markdown?**  
A: Нет, HTML фильтруется из соображений безопасности.

**Q: Поддерживаются ли формулы?**  
A: В текущей версии нет, но планируется добавить LaTeX/MathJax.

**Q: Как импортировать карточки с Markdown из Anki?**  
A: Экспортируйте из Anki в CSV, сохраняя HTML/Markdown форматирование.
