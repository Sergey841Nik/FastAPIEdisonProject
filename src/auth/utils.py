from datetime import datetime, timezone, timedelta
from logging import getLogger

import bcrypt
import jwt

from src.core.config import settings

logger = getLogger(__name__)


def encode_jwt(
    payload: dict,
    type_token: str,
    private_key: str = settings.private_key_path.read_text(),
    algorithm: str = settings.algorithms,
) -> str:
    now: datetime = datetime.now(timezone.utc)
    if type_token == "access":
        expires: datetime = now + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    elif type_token == "refresh":
        expires: datetime = now + timedelta(days=settings.refresh_token_expire_days)
    else:
        raise ValueError("Неизвестный тип токена")
    to_encode: dict = payload.copy()
    to_encode.update(exp=expires, iat=now)

    return jwt.encode(to_encode, private_key, algorithm=algorithm)


def decode_jwt(
    token: str | bytes,
    public_key: str = settings.public_key_path.read_text(),
    algorithm: str = settings.algorithms,
) -> dict:
    return jwt.decode(token, public_key, algorithms=[algorithm])


def hash_password(password: str) -> bytes:
    salt: bytes = bcrypt.gensalt()
    password_bytes: bytes = password.encode()
    return bcrypt.hashpw(password_bytes, salt)


def validate_password(password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password)
