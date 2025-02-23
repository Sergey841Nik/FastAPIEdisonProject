from logging import getLogger, basicConfig, INFO, StreamHandler

import uvicorn

from fastapi import FastAPI

from src.auth.views import router as auth_router

app = FastAPI()

logger = getLogger()

FORMAT = "%(asctime)s:%(levelname)s:%(name)s:%(message)s"

stream_handler = StreamHandler()
stream_handler.setLevel(INFO)
basicConfig(level=INFO, format=FORMAT, handlers=[stream_handler])

app.include_router(auth_router)


@app.get("/")
def home_page():
    return {"message": "Это стартовое сообщение"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        reload=True,
    )

