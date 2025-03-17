
from fastapi import APIRouter, UploadFile, File, Depends, status

from src.api_predictions.schemas import PredictionResponse
from src.auth.dependencies import get_current_token_payload

from src.api_predictions.predictions_img import process_image_prediction

router = APIRouter(prefix="/predictions", tags=["predictions"])

@router.post("/predict/", response_model=PredictionResponse, status_code=status.HTTP_200_OK)
async def predict_endpoint(
    file: UploadFile = File(...),
    payload: dict = Depends(get_current_token_payload),
) -> PredictionResponse:
    file_content: bytes = await file.read()
    fail_name: str = file.filename
    return process_image_prediction(file_content, fail_name)
   

# @router.get("/health/", status_code=status.HTTP_200_OK)
# async def health_check():
#     """Эндпоинт для проверки доступности сервиса предсказаний"""
#     return {"status": "ok", "model_loaded": model is not None}