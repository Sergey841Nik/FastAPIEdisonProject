from logging import Logger, getLogger, basicConfig, INFO, StreamHandler, FileHandler
from pathlib import Path

from starlette.templating import _TemplateResponse
import uvicorn

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request

from src.auth.views import router as auth_router
from src.api_predictions.views import router as predictions_router
from src.exceptions import (
    custom_http_exception_handler,
    custom_request_validation_exception_handler,
)

# Определение путей
BASE_DIR: Path = Path(__file__).parent.parent
TEMPLATES_DIR: Path = BASE_DIR / "templates"
STATIC_DIR: Path = BASE_DIR / "static"
LOG_FILE: Path = BASE_DIR / "logs.log"

# Создание экземпляра FastAPI приложения
app = FastAPI()

# Настройка логгера
logger: Logger = getLogger(__name__)

# Формат логов
FORMAT = "%(asctime)s:%(levelname)s:%(name)s:%(message)s"

# Настройка обработчиков для вывода логов
stream_handler = StreamHandler()
file_handler = FileHandler(LOG_FILE, encoding="utf-8")

# Установка уровня логирования
stream_handler.setLevel(INFO)
file_handler.setLevel(INFO)

# Настройка базовой конфигурации логгера
basicConfig(level=INFO, format=FORMAT, handlers=[stream_handler, file_handler])

# Подключение статических файлов
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Подключение шаблонов
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Подключение роутеров
app.include_router(auth_router)  # Роутер для аутентификации
app.include_router(predictions_router)  # Роутер для предсказаний

# Регистрация обработчиков исключений
app.add_exception_handler(HTTPException, custom_http_exception_handler)
app.add_exception_handler(
    RequestValidationError, custom_request_validation_exception_handler
)


@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request) -> _TemplateResponse:
    """
    Корневой эндпоинт приложения
    Возвращает HTML страницу
    """
    logger.info("Запрос к главной странице")
    return templates.TemplateResponse("index.html", {"request": request})


if __name__ == "__main__":
    # Запуск сервера разработки
    logger.info("Запуск сервера разработки")
    uvicorn.run(
        "main:app",
        reload=True,  # Автоматическая перезагрузка при изменении кода
        host="0.0.0.0",
        port=8000,  # Порт сервера
    )
