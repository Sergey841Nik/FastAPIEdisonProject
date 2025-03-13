from logging import Logger, getLogger
from typing import Any

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger: Logger = getLogger(__name__)


async def custom_http_exception_handler(
    request: Request, exc: HTTPException
) -> JSONResponse:
    logger.error("Ошибка http: %s", exc)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error http": str(exc)},
    )


async def custom_request_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "message": "Собственный проверяльщик ошибок валидации",
            "errors": exc.errors(),
        },
    )

def valid_integer(value: Any) -> bool:
    if not isinstance(value, int):
        raise TypeError("Значение должно быть целым числом")
    return True

def valid_string(value: Any) -> bool:
    if not isinstance(value, str):
        raise TypeError("Значение должно быть строкой")
    return True