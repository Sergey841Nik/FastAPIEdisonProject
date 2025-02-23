from logging import getLogger

from fastapi import Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError

from src.auth.shemas import UserBase
from src.auth import utils

logger = getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

user1 = UserBase(email="john@example.com", name="john")
user2 = UserBase(email="jane@example.com", name="jane")

users_db = {user1.email: user1, user2.email: user2}

def create_jwt(
    token_data: dict,
    token_type: str,
) -> str:
    jwt_payload = {"type": token_type}
    jwt_payload.update(token_data)
    logger.info("Создание токена c такой информацией %s" % jwt_payload)
    return utils.encode_jwt(
        payload=jwt_payload,
        type_token=token_type,
    )


def create_access_token(user: UserBase) -> str:
    jwt_payload = {
        "sub": user.email,
        "username": user.name,
    }
    logger.info("Создание аксесс для %s" % user.email)
    return create_jwt(
        token_data=jwt_payload,
        token_type="access",
    )


def create_refresh_token(user: UserBase) -> str:
    jwt_payload = {
        "sub": user.email,
    }
    logger.info("Создание рефреш для %s" % user.email)
    return create_jwt(
        token_data=jwt_payload,
        token_type="refresh",
    )

def validate_type_token(payload: dict, token_type: str) -> bool:
    if payload.get("type") == token_type:
        return True
    raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"token type invalid {payload.get('type')!r} expected {token_type!r}"
        )

def get_current_token_payload(token: str = Depends(oauth2_scheme)) -> UserBase:
    try:
        payload = utils.decode_jwt(token=token)
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"invalid token error {e}"
            )
    return payload


def get_user_by_token_sub(payload: dict) -> UserBase:
    email: str | None = payload.get("sub")
    if user := users_db.get(email):
        return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="token invalid"
    )


# юзер для аксеса с проверкой типа токена
def get_current_auth_user(
    payload: dict = Depends(get_current_token_payload),
) -> UserBase:
    validate_type_token(payload, "access")
    return get_user_by_token_sub(payload)


# юзер для рефреша с проверкой типа токена
def get_current_auth_user_for_refresh(
    payload: dict = Depends(get_current_token_payload),
) -> UserBase:

    validate_type_token(payload, "refresh")
    return get_user_by_token_sub(payload)


def validate_auth_user(
        email: str = Form(),
        name: str = Form(),
):
    unauthed_exc = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail= "Invalid username or password",
    ) 

    if not (user := users_db.get(email)):
        raise unauthed_exc
    logger.info("Пользователь найден %s" % user)
    return user


 
