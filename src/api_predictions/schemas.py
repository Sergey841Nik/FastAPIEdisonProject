from pydantic import BaseModel
from typing import List


class Detection(BaseModel):
    class_name: str
    confidence: float
    box: List[int]  # [x1, y1, x2, y2]


class PredictionResponse(BaseModel):
    """Модель ответа для предсказания изображения"""
    detections: List[Detection]
    processed_image: bytes  # base64 encoded image
