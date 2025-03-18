from calendar import timegm
from contextlib import nullcontext
from datetime import datetime, timedelta, timezone
import pytest
from src.auth.utils import encode_jwt, decode_jwt, hash_password, validate_password


@pytest.mark.parametrize(
    "user_id, user_name, type_token, expectation",
    (
        (1, "test_user", "access", nullcontext()),
        (25, "user1", "access", nullcontext()),
        (35, "user2", "access", nullcontext()),
        (
            45,
            "user3",
            "unknown",
            pytest.raises(ValueError, match="Неизвестный тип токена"),
        ),
    ),
)
def test_encode_jwt_access_token(user_id, user_name, type_token, expectation) -> None:
    payload: dict = {"user_id": user_id, "username": user_name}
    with expectation:
        token: str = encode_jwt(payload, type_token)

        assert isinstance(token, str)

        decode_payload: dict = decode_jwt(token)
        now: datetime = datetime.now(timezone.utc)

        assert decode_payload["user_id"] == user_id
        assert decode_payload["username"] == user_name
        # assert datetime.fromtimestamp(decode_payload["exp"]).day == (now + timedelta(minutes=15)).day
        assert decode_payload["iat"] == timegm((now).utctimetuple())


@pytest.mark.parametrize(
    "user_id, user_name, type_token, expectation",
    (
        (1, "test_user", "refresh", nullcontext()),
        (25, "user1", "refresh", nullcontext()),
        (35, "user2", "refresh", nullcontext()),
        (
            45,
            "user3",
            "unknown",
            pytest.raises(ValueError, match="Неизвестный тип токена"),
        ),
    ),
)
def test_encode_jwt_refresh_token(user_id, user_name, type_token, expectation) -> None:
    payload: dict = {"user_id": user_id, "username": user_name}
    with expectation:
        token: str = encode_jwt(payload, type_token)

        assert isinstance(token, str)

        decode_payload: dict = decode_jwt(token)
        now: datetime = datetime.now(timezone.utc)

        assert decode_payload["user_id"] == user_id
        assert decode_payload["username"] == user_name
        assert datetime.fromtimestamp(decode_payload["exp"]).day == (now + timedelta(days=7)).day
        assert decode_payload["iat"] == timegm((now).utctimetuple())


def test_validate_password() -> None:
    password = "test_password"
    hashed_password: bytes = hash_password(password)

    assert isinstance(hashed_password, bytes)
    assert validate_password(password, hashed_password) is True


    