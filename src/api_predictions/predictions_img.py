import os
import shutil

import tensorflow as tf
import tensorflow_hub as hub
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout, InputLayer
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.optimizers import Adam
import numpy as np
from pathlib import Path
from PIL import Image

from logging import Logger, getLogger

from fastapi import HTTPException, status

from src.api_predictions.schemas import PredictionResponse

# Настройка логгера
logger: Logger = getLogger(__name__)

# Константы
BASE_DIR = Path(__file__).parent.parent.parent
MODEL_PATH = BASE_DIR / "src" / "api_predictions" / "my_image_classifier.h5"
TEMP_DIR = BASE_DIR / "src" / "api_predictions" / "temp"

# Создаем временную директорию, если она не существует
os.makedirs(TEMP_DIR, exist_ok=True)

# Параметры изображения
IMG_HEIGHT = 224
IMG_WIDTH = 224
BATCH_SIZE = 32


def create_model():
    """Создает модель на основе предобученной модели из TensorFlow Hub"""
    logger.info("Загружаем предобученную модель из TensorFlow Hub...")

    # Используем MobileNet V2, предобученную на ImageNet
    # Эта модель хорошо работает для классификации изображений и достаточно легкая
    mobilenet_url = "https://tfhub.dev/google/tf2-preview/mobilenet_v2/classification/4"

    # Создаем модель
    hub_model = hub.KerasLayer(mobilenet_url, input_shape=(IMG_HEIGHT, IMG_WIDTH, 3))

    model = Sequential(
        [
            InputLayer(input_shape=(IMG_HEIGHT, IMG_WIDTH, 3)),
            hub_model,
            Dense(1, activation="sigmoid"),  # Бинарная классификация (кошка или собака)
        ]
    )

    # Компилируем модель
    model.compile(
        optimizer=Adam(learning_rate=0.0001),
        loss="binary_crossentropy",
        metrics=["accuracy"],
    )

    # Сохраняем модель
    model.save(MODEL_PATH)
    logger.info("Модель сохранена по пути: %s", MODEL_PATH)

    return model


def load_or_create_model():
    """Загружает существующую модель или создает новую"""
    if os.path.exists(MODEL_PATH):
        logger.info("Загружаем существующую модель из %s", MODEL_PATH)
        return tf.keras.models.load_model(
            MODEL_PATH, custom_objects={"KerasLayer": hub.KerasLayer}
        )
    else:
        logger.info("Модель не найдена. Создаем новую модель...")
        return create_model()


def preprocess_image(image_path):
    """Предобработка изображения для предсказания"""
    try:
        img = Image.open(image_path)
        img = img.resize((IMG_HEIGHT, IMG_WIDTH))
        img_array = tf.keras.preprocessing.image.img_to_array(img)
        img_array = img_array / 255.0  # Нормализация
        img_array = np.expand_dims(img_array, axis=0)
        return img_array
    except Exception as e:
        logger.error("Ошибка при предобработке изображения: %s", e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не удалось обработать изображение",
        )


def predict_image(model, image_path):
    """Делает предсказание для изображения"""
    try:
        img_array = preprocess_image(image_path)
        prediction = model.predict(img_array)
        score = float(prediction[0][0])

        # Интерпретируем результат (бинарная классификация)
        # Для MobileNet, значения ближе к 0 обычно соответствуют кошкам, а ближе к 1 - собакам
        if score < 0.5:
            class_name = "кошка"
            confidence = 1 - score
        else:
            class_name = "собака"
            confidence = score

        return PredictionResponse(
            class_name=class_name, confidence=round(confidence * 100, 2)
        )
    except Exception as e:
        logger.error("Ошибка при предсказании: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при выполнении предсказания",
        )

def process_image_prediction(file_content: bytes, filename: str) -> PredictionResponse:
    """Получаем модель"""
    model = load_or_create_model()
    """Обрабатывает предсказание для изображения"""
    try:
        logger.info("Запросил предсказание для файла %s", filename)

        # Сохраняем загруженный файл во временную директорию
        temp_file_path: Path = TEMP_DIR / filename
        with open(temp_file_path, "wb") as buffer:
            buffer.write(file_content)

        # Делаем предсказание
        result: PredictionResponse = predict_image(model, temp_file_path)

        # Удаляем временный файл
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

        logger.info("Предсказание для %s: %s", filename, result)
        return result

    except Exception as e:
        logger.error("Ошибка при обработке запроса: %s", e)
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обработке запроса: {str(e)}",
        )
