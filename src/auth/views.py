
from fastapi import APIRouter, Depends

from src.auth.dependencies import validate_auth_user, create_access_token, create_refresh_token
from src.auth.shemas import UserBase, TokenInfo

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login/", response_model=TokenInfo)
def auth_user_issue_jwt(
    user: UserBase = Depends(validate_auth_user),
):
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    return TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token,)