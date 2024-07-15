from fastapi import Depends

from crud import get_crud_auth_user, get_crud_refresh_token, get_crud_otp
from services.auth_service import AuthUserService


def auth_user_service(
    crud_auth_user=Depends(get_crud_auth_user),
    crud_refresh_token=Depends(get_crud_refresh_token),
    crud_otp=Depends(get_crud_otp),
) -> AuthUserService:
    return AuthUserService(
        crud_auth_user=crud_auth_user,
        crud_refresh_token=crud_refresh_token,
        crud_otp=crud_otp,
    )
