# Импорт необходимых модулей
from logging import Logger, getLogger
from typing import Any

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# Инициализация логгера для модуля
logger: Logger = getLogger(__name__)


async def custom_http_exception_handler(
    request: Request, exc: HTTPException
) -> JSONResponse:
    """
    Обработчик HTTP исключений
    Логирует ошибку и возвращает JSON-ответ с информацией об ошибке
    """
    logger.error("Ошибка http: %s", exc)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error http": str(exc)},
    )


async def custom_request_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Обработчик ошибок валидации запросов
    Возвращает детальную информацию об ошибках валидации
    """
    return JSONResponse(
        status_code=422,
        content={
            "message": "Собственный проверяльщик ошибок валидации",
            "errors": exc.errors(),
        },
    )


def valid_integer(value: Any) -> bool:
    """
    Валидатор для проверки целочисленных значений
    Выбрасывает TypeError если значение не является целым числом
    """
    if not isinstance(value, int):
        raise TypeError("Значение должно быть целым числом")
    return True


def valid_string(value: Any) -> bool:
    """
    Валидатор для проверки строковых значений
    Выбрасывает TypeError если значение не является строкой
    """
    if not isinstance(value, str):
        raise TypeError("Значение должно быть строкой")
    return True