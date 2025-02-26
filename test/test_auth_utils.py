from calendar import timegm
import pytest
from datetime import datetime, timedelta, timezone
from src.auth.utils import encode_jwt, decode_jwt, hash_password, validate_password


def test_encode_jwt_access_token() -> None:
    payload: dict = {"user_id": 25, "username": "test_user"}
    type_token = "access"

    token: str = encode_jwt(payload, type_token)

    assert isinstance(token, str)

    decode_payload: dict = decode_jwt(token)
    now: datetime = datetime.now(timezone.utc)

    assert decode_payload["user_id"] == 25
    assert decode_payload["username"] == "test_user"
    assert decode_payload["exp"] == timegm((now + timedelta(minutes=15)).utctimetuple())
    assert decode_payload["iat"] == timegm((now).utctimetuple())


def test_encode_jwt_refresh_token() -> None:
    payload: dict = {"user_id": 1, "username": "test_user"}
    type_token: str = "refresh"

    token: str = encode_jwt(payload, type_token)

    assert isinstance(token, str)

    decode_payload: dict = decode_jwt(token)
    now: datetime = datetime.now(timezone.utc)

    assert decode_payload["user_id"] == 1
    assert decode_payload["username"] == "test_user"
    assert decode_payload["exp"] == timegm((now + timedelta(days=30)).utctimetuple())
    assert decode_payload["iat"] == timegm((now).utctimetuple())


def test_encode_jwt_unknown_token_type() -> None:
    payload = {"user_id": 1, "username": "test_user"}
    type_token = "unknown"

    with pytest.raises(ValueError, match="Неизвестный тип токена"):
        encode_jwt(payload, type_token)


def test_validate_password() -> None:
    password = "test_password"
    hashed_password = hash_password(password)
    
    assert validate_password(password, hashed_password) is True
