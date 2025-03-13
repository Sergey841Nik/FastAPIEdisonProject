from typing import Optional
from logging import Logger, getLogger
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Response, Request, Depends, HTTPException, status, Form

from src.auth.dependencies import (
    validate_auth_user,
    create_access_token,
    create_refresh_token,
    get_current_auth_user,
    get_current_auth_user_for_refresh,
    get_current_token_payload,
    get_current_admin_user,
    get_all_users_for_admin,
    update_user,
    delete_user,
)
from src.auth.schemas import (
    TokenInfo,
    UserBase,
    UserInfoForAdmin,
    UserRegister,
    UserAddDB,
    UserInfo,
    UserUpdate,
    UserUpdateInfo,
)
from src.auth.dao import AuthDao
from src.core.db_helper import db_helper

router = APIRouter(prefix="/auth", tags=["auth"])

logger: Logger = getLogger(__name__)


@router.post("/register/", status_code=status.HTTP_201_CREATED)
async def register_users(
    user: UserRegister,
    session: AsyncSession = Depends(db_helper.get_session_with_commit),
) -> dict:
    dao = AuthDao(session=session)
    find_user = await dao.find_one_or_none(user.email)
    if find_user:
        logger.info("Запись %s найдена", find_user)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Пользователь уже существует"
        )

    user_dict = user.model_dump()
    del user_dict["confirm_password"]

    res = await dao.add(UserAddDB(**user_dict))
    logger.info("Запись %s ", res)
    return {"message": "Вы успешно зарегистрированы!"}


@router.post("/login/", response_model=TokenInfo)
async def auth_user_issue_jwt(
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    # user_data: OAuth2PasswordRequestForm = Depends(),
    session=Depends(db_helper.get_session_without_commit),
) -> TokenInfo:

    user: UserInfo = await validate_auth_user(
        session=session, email=username, password=password
    )

    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,  # Только для HTTPS
        samesite="strict",  # Защита от CSRF
    )
    return TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token,
    )

@router.post(
    "/refresh/",
    response_model=TokenInfo,
    response_model_exclude_none=True,  # если в есть значения none то исключаем эти поля (тут refresh_token будет none)
)
async def auth_refresh_jwt(
    request: Request,
    session: AsyncSession = Depends(db_helper.get_session_without_commit),
) -> TokenInfo:
    token: str | None = request.cookies.get("refresh_token")
    payload: dict = get_current_token_payload(token=token)
    user: UserBase = await get_current_auth_user_for_refresh(
        session=session, payload=payload
    )
    user_update = UserInfo(**user.model_dump(), id=payload["sub"])
    print(f"{user_update=}")
    access_token: str = create_access_token(user_update)
    return TokenInfo(
        access_token=access_token,
    ) 


@router.get("/user/me/", response_model=UserBase)
async def get_user_info(
    session: AsyncSession = Depends(db_helper.get_session_without_commit),
    payload: dict = Depends(get_current_token_payload),
) -> UserBase:
    user: UserBase = await get_current_auth_user(session=session, payload=payload)

    return user

@router.put("/user/me/update_user/")
async def update_user_info(
    email_name: UserUpdate,
    session: AsyncSession = Depends(db_helper.get_session_with_commit),
    payload: dict = Depends(get_current_token_payload),
) -> dict:
    uses = UserUpdateInfo(**email_name.model_dump(), user_id=int(payload.get("sub")))
    await update_user(session=session, user=uses)
    return {"message": "Данные успешно обновлены"}

@router.get("/all_users_for_admin/", response_model=list[UserInfoForAdmin])
async def get_all_users(
    session: AsyncSession = Depends(db_helper.get_session_without_commit),
    payload: dict = Depends(get_current_token_payload),
) -> list[UserInfoForAdmin]:
    if await get_current_admin_user(session=session, payload=payload):
        return await get_all_users_for_admin(session=session)
