import os
import base64
from logging import Logger, getLogger

import cv2
import numpy as np
from pathlib import Path
from fastapi import HTTPException, status

from src.api_predictions.schemas import PredictionResponse, Detection

# Настройка логгера
logger: Logger = getLogger(__name__)

# Константы
BASE_DIR = Path(__file__).parent.parent.parent
TEMP_DIR = BASE_DIR / "src" / "api_predictions" / "temp"
MODEL_PATH = BASE_DIR / "src" / "api_predictions" / "mobilenet_iter_73000.caffemodel"
CONFIG_PATH = BASE_DIR / "src" / "api_predictions" / "mobilenet_ssd_deploy.prototxt"

# Создаем временную директорию, если она не существует
os.makedirs(TEMP_DIR, exist_ok=True)

# Метки классов PASCAL VOC
VOC_LABELS = [
    "background", "aeroplane", "bicycle", "bird", "boat", "bottle",
    "bus", "car", "cat", "chair", "cow", "diningtable",
    "dog", "horse", "motorbike", "person", "pottedplant",
    "sheep", "sofa", "train", "tvmonitor"
]

def process_image_prediction(file_content: bytes, filename: str) -> PredictionResponse:
    """Обрабатывает предсказание для изображения"""
    try:
        logger.info("Запросил предсказание для файла %s", filename)

        # Сохраняем загруженный файл во временную директорию
        temp_file_path: Path = TEMP_DIR / filename
        with open(temp_file_path, "wb") as buffer:
            buffer.write(file_content)

        # Загружаем модель
        net = cv2.dnn.readNetFromCaffe(str(CONFIG_PATH), str(MODEL_PATH))

        # Читаем изображение
        img = cv2.imread(str(temp_file_path))
        if img is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не удалось загрузить изображение"
            )

        h, w = img.shape[:2]
        blob = cv2.dnn.blobFromImage(img, 0.007843, (300, 300), 127.5)

        # Делаем предсказание
        net.setInput(blob)
        detections = net.forward()

        # Обрабатываем все найденные объекты
        found_detections = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.6:
                class_id = int(detections[0, 0, i, 1])
                class_label = VOC_LABELS[class_id]
                
                # Получаем координаты рамки
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                
                # Рисуем рамку и подпись
                cv2.rectangle(img, (startX, startY), (endX, endY), (0, 255, 0), 2)
                label = f"{class_label}: {confidence:.2f}"
                cv2.putText(img, label, (startX + 5, startY + 15), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                found_detections.append(Detection(
                    class_name=class_label,
                    confidence=float(confidence),
                    box=[int(startX), int(startY), int(endX), int(endY)]
                ))

        if not found_detections:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не удалось определить объекты на изображении"
            )

        # Кодируем обработанное изображение в base64
        _, buffer = cv2.imencode('.jpg', img)
        processed_image = base64.b64encode(buffer).decode('utf-8')

        # Удаляем временный файл
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

        logger.info("Найдено объектов: %d", len(found_detections))
        return PredictionResponse(
            detections=found_detections,
            processed_image=processed_image
        )

    except Exception as e:
        logger.error("Ошибка при обработке запроса: %s", e)
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обработке запроса: {str(e)}"
        )
