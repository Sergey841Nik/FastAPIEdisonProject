# FastAPI Edison Project

Веб-приложение на FastAPI с аутентификацией и возможностями предсказания.

## Технологический стек

- Python 3.12
- FastAPI (веб-фреймворк)
- SQLAlchemy (ORM для работы с базой данных)
- Alembic (миграции базы данных)
- Pydantic (валидация данных)
- JWT Authentication (аутентификация)
- OpenCV (обработка изображений)
- Poetry (управление зависимостями)
- Docker (контейнеризация)

## Структура проекта

```
.
├── alembic/           # Миграции базы данных
├── src/              # Исходный код
│   ├── api_predictions/  # API эндпоинты для предсказаний
│   ├── auth/           # Модуль аутентификации
│   ├── core/          # Основной функционал
│   └── main.py        # Точка входа приложения
├── tests/            # Тесты
├── .env              # Переменные окружения
├── .env_test         # Переменные окружения для тестов
├── compose.yml       # Конфигурация Docker Compose
├── pyproject.toml    # Зависимости Poetry
└── pytest.ini       # Конфигурация Pytest
```

## Установка

1. Установите Poetry:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Установите зависимости:
```bash
poetry install
```

3. Настройте переменные окружения:
```bash
cp .env
# Отредактируйте .env под вашу конфигурацию
```

4. Создайте ключи для JWT аутентификации:
```bash
# Создание директории в корне проекта и переход в директорию
mkdir -p cert
cd /cert

# Создание приватного ключа
openssl genrsa -out private.pem 2048

# Создание публичного ключа на основе приватного
openssl rsa -in private.pem -pubout -out public.pem
```

5. Запустите миграции базы данных:
```bash
alembic upgrade head
```

## Запуск приложения

Разработка:
```bash
uvicorn src.main:app --reload
```

Продакшн:
```bash
docker compose up -d
```

## Тестирование

Запуск тестов:
```bash
pytest
```

## Документация API

После запуска приложения доступны:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Возможности

- Аутентификация через JWT
- Управление пользователями
- API эндпоинты для предсказаний
- Миграции базы данных через Alembic
- Полный набор тестов
- Поддержка Docker
- Система логирования
