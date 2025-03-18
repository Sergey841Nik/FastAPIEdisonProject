# FastAPI Edison Project

Проект на FastAPI для распознавания объектов на изображениях с использованием нейронной сети MobileNet-SSD.

## Технологический стек

### Backend
- Python 3.11+
- FastAPI
- SQLAlchemy
- OpenCV
- MobileNet-SSD
- JWT аутентификация
- PostgreSQL

### Frontend
- HTML5
- CSS3
- JavaScript (Vanilla)
- FormData для загрузки файлов
- Base64 для отображения обработанных изображений

## Структура проекта

```
FastAPI_Edison/
├── src/
│   ├── api_predictions/     # Модуль для работы с предсказаниями
│   ├── auth/               # Модуль аутентификации
│   ├── core/               # Основные настройки и утилиты
│   └── main.py            # Точка входа приложения
├── static/                 # Статические файлы
│   ├── css/               # Стили
│   └── js/                # JavaScript файлы
├── templates/             # HTML шаблоны
├── cert/                  # Сертификаты для JWT
├── requirements.txt       # Зависимости проекта
└── README.md             # Документация
```

## Установка и настройка

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd FastAPI_Edison
```

2. Создайте виртуальное окружение и активируйте его:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
# или
venv\Scripts\activate  # для Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл `.env` в корневой директории проекта:
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
SECRET_KEY=your-secret-key
ALGORITHM=RS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

5. Создайте базу данных PostgreSQL и примените миграции:
```bash
alembic upgrade head
```

6. Сгенерируйте ключи для JWT:
```bash
# Создание приватного ключа
openssl genrsa -out cert/private.pem 2048

# Создание публичного ключа
openssl rsa -in cert/private.pem -pubout -out cert/public.pem
```

## Запуск проекта

1. Запустите сервер разработки:
```bash
uvicorn src.main:app --reload
```

2. Откройте браузер и перейдите по адресу:
```
http://localhost:8000
```

## Функциональность

### Backend
- Аутентификация пользователей (JWT)
- Загрузка и обработка изображений
- Распознавание объектов с помощью MobileNet-SSD
- API для получения предсказаний
- Логирование операций

### Frontend
- Современный адаптивный дизайн
- Форма авторизации
- Загрузка изображений через drag-and-drop
- Отображение обработанных изображений с рамками и подписями
- Вывод информации о найденных объектах
- Управление состоянием авторизации

## API Документация

После запуска сервера документация доступна по адресам:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Тестирование

Для запуска тестов выполните:
```bash
pytest
```
