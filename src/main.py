from logging import getLogger, basicConfig, INFO, StreamHandler

import uvicorn

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError, HTTPException

from src.auth.views import router as auth_router
from src.exceptions import (
    custom_http_exception_handler,
    custom_request_validation_exception_handler,
)

app = FastAPI()

logger = getLogger()

FORMAT = "%(asctime)s:%(levelname)s:%(name)s:%(message)s"

stream_handler = StreamHandler()
stream_handler.setLevel(INFO)
basicConfig(level=INFO, format=FORMAT, handlers=[stream_handler])

app.include_router(auth_router)

app.add_exception_handler(HTTPException, custom_http_exception_handler)
app.add_exception_handler(RequestValidationError, custom_request_validation_exception_handler)

@app.get("/")
def home_page() -> dict:
    return {"message": "Это стартовое сообщение"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        reload=True,
        port=8000,
    )

