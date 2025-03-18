# Импорт необходимых модулей для логирования
from logging import Logger, getLogger, basicConfig, INFO, StreamHandler

import uvicorn

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError, HTTPException

# Импорт роутеров из модулей
from src.auth.views import router as auth_router
from src.api_predictions.views import router as predictions_router
from src.exceptions import (
    custom_http_exception_handler,
    custom_request_validation_exception_handler,
)

# Создание экземпляра FastAPI приложения
app = FastAPI()

# Настройка логгера
logger: Logger = getLogger()

# Формат логов
FORMAT = "%(asctime)s:%(levelname)s:%(name)s:%(message)s"

# Настройка обработчика для вывода логов в консоль
stream_handler = StreamHandler()
stream_handler.setLevel(INFO)
basicConfig(level=INFO, format=FORMAT, handlers=[stream_handler])

# Подключение роутеров
app.include_router(auth_router)  # Роутер для аутентификации
app.include_router(predictions_router)  # Роутер для предсказаний

# Регистрация обработчиков исключений
app.add_exception_handler(HTTPException, custom_http_exception_handler)
app.add_exception_handler(
    RequestValidationError, custom_request_validation_exception_handler
)


@app.get("/")
def home_page() -> dict:
    """
    Корневой эндпоинт приложения
    Возвращает приветственное сообщение
    """
    return {"message": "Это стартовое сообщение"}


if __name__ == "__main__":
    # Запуск сервера разработки
    uvicorn.run(
        "main:app",
        reload=True,  # Автоматическая перезагрузка при изменении кода
        port=8000,    # Порт сервера
    )
