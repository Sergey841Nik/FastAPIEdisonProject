from pydantic import BaseModel, Field, ConfigDict


class PredictionResponse(BaseModel):
    """Модель ответа для предсказания изображения"""
    class_name: str = Field(description="Класс изображения (кошка или собака)")
    confidence: float = Field(description="Уверенность в предсказании в процентах", ge=0, le=100)
