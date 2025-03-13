from logging import Logger, getLogger
from typing import Any

from sqlalchemy import Row
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError

from src.auth.schemas import UserInfo, UserBase, UserInfoForAdmin, UserUpdateInfo
from src.auth import utils
from src.auth.dao import AuthDao

logger: Logger = getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login/")


def create_jwt(
    token_data: dict,
    token_type: str,
) -> str:
    jwt_payload: dict = {"type": token_type}
    jwt_payload.update(token_data)
    logger.info("Создание токена c информацией %s", jwt_payload)
    return utils.encode_jwt(
        payload=jwt_payload,
        type_token=token_type,
    )


def create_access_token(user: UserInfo) -> str:
    jwt_payload: dict = {
        "sub": str(user.id),
        "email": user.email,
    }

    logger.info("Создание аксесс для %s", user.email)
    return create_jwt(
        token_data=jwt_payload,
        token_type="access",
    )


def create_refresh_token(user: UserInfo) -> str:
    jwt_payload: dict = {
        "sub": str(user.id),
    }
    logger.info("Создание рефреш для %s", user.email)
    return create_jwt(
        token_data=jwt_payload,
        token_type="refresh",
    )


def validate_type_token(payload: dict, token_type: str) -> bool:
    if payload.get("type") == token_type:
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"token type invalid {payload.get('type')!r} expected {token_type!r}",
    )


def get_current_token_payload(token: str = Depends(oauth2_scheme)) -> dict:
    logger.info("Получаем payload из токена %s", token)
    try:
        payload: dict = utils.decode_jwt(token=token)
        logger.info("Расшифрованные данные %s", payload)
    except InvalidTokenError as e:
        logger.info("Ошибка %s", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"invalid token error {e}"
        )
    return payload


async def get_user_by_token_sub(
    session: AsyncSession,
    payload: dict,
) -> UserBase:
    dao = AuthDao(session)
    if user := await dao.find_one_or_none_by_id(int(payload.get("sub"))):
        return UserBase(email=user[2], name=user[1])
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


# юзер для аксеса с проверкой типа токена
async def get_current_auth_user(
    session: AsyncSession,
    payload: dict,
) -> UserBase:
    logger.info("payload access: %s", payload)
    validate_type_token(payload, "access")
    user: UserBase = await get_user_by_token_sub(session=session, payload=payload)
    return user

async def update_user(
    session: AsyncSession,
    user: UserUpdateInfo,
) -> None:
    
    dao = AuthDao(session)
    logger.info("Обновляемые данные: %s", user)
    await dao.update(model=user)


async def get_current_admin_user(
    session: AsyncSession,
    payload: dict,
) -> bool:
    dao = AuthDao(session)
    user_roles: str | None = await dao.get_roles_user(int(payload.get("sub")))
    if user_roles == "adminishe":
        return True
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="У вас недостаточно прав"
    )

async def get_all_users_for_admin(
    session: AsyncSession,
) -> list[UserInfoForAdmin]:
    dao = AuthDao(session)
    users = await dao.find_all()
    return [UserInfoForAdmin(id=user[0], email=user[2], name=user[1], roles_name=user[3]) for user in users]


# юзер для рефреша с проверкой типа токена
async def get_current_auth_user_for_refresh(
    session: AsyncSession,
    payload: dict,
) -> UserBase:
    logger.info("payload refresh: %s", payload)
    validate_type_token(payload, "refresh")
    user: UserBase = await get_user_by_token_sub(session=session, payload=payload)
    return user


async def validate_auth_user(
    session: AsyncSession,
    email: str,
    password: str,
) -> UserInfo:

    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
    )
    dao = AuthDao(session)
    user: Row[Any] | None = await dao.find_one_or_none(email)

    if not user:
        raise unauthed_exc
    if not utils.validate_password(password, user[3]):
        raise unauthed_exc

    logger.info("Пользователь найден %s", user)
    user = UserInfo(id=user[0], email=user[2], name=user[1])
    return user
