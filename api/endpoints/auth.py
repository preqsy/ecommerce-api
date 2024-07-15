from fastapi import APIRouter, Depends, BackgroundTasks, Header, Query, status
from fastapi.security import OAuth2PasswordRequestForm

from core.schema import Tokens
from core.tokens import (
    deactivate_token,
    get_current_auth_user,
    regenerate_tokens,
)

from schemas import (
    AuthUserCreate,
    AuthUserResponse,
    LogoutResponse,
    RegisterAuthUserResponse,
    TokenDeactivate,
    OtpVerified,
    OTPCreate,
    NewPassword,
    EmailIn,
    ForgotPassword,
    ResetPassword,
    RefreshTokenSchema,
    ChangePassword,
    PasswordChanged,
)
from models import AuthUser
from services import AuthUserService
from api.dependencies.services import get_auth_user_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=RegisterAuthUserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    data_obj: AuthUserCreate,
    background_task: BackgroundTasks,
    user_agent: str = Header(None),
    auth_user_service: AuthUserService = Depends(get_auth_user_service),
):

    return await auth_user_service.register_auth_user(
        data_obj=data_obj, user_agent=user_agent, background_task=background_task
    )


@router.post("/verify", response_model=OtpVerified)
async def verify_email_or_phone(
    data_obj: OTPCreate,
    auth_user_service: AuthUserService = Depends(get_auth_user_service),
):

    return await auth_user_service.verify(data_obj=data_obj)


@router.post("/token", status_code=status.HTTP_201_CREATED, response_model=Tokens)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_agent: str = Header(None),
    auth_user_service: AuthUserService = Depends(get_auth_user_service),
):

    return await auth_user_service.login_user(
        form_data=form_data, user_agent=user_agent
    )


@router.post("/logout", status_code=status.HTTP_200_OK, response_model=LogoutResponse)
async def logout_user(
    token: TokenDeactivate,
    current_user: AuthUser = Depends(get_current_auth_user),
):
    await deactivate_token(token.access_token, auth_id=current_user.id)
    return LogoutResponse(logout=True)


@router.post("/forget-password", response_model=ForgotPassword)
async def forget_password(
    data_obj: EmailIn,
    background_tasks: BackgroundTasks,
    user_agent: str = Header(None),
    auth_user_service: AuthUserService = Depends(get_auth_user_service),
):
    return await auth_user_service.forget_password(
        data_obj, user_agent, background_tasks
    )


@router.post("/reset-password", response_model=ResetPassword)
async def reset_password(
    data_obj: NewPassword,
    token: str = Query(),
    auth_user_service: AuthUserService = Depends(get_auth_user_service),
):

    return await auth_user_service.reset_password(data_obj=data_obj, token=token)


@router.get("/me", response_model=AuthUserResponse)
async def get_me(
    current_user: AuthUser = Depends(get_current_auth_user),
):

    return current_user


@router.post("/refresh-token", response_model=Tokens)
async def refresh_access_token(
    token: RefreshTokenSchema,
    current_user: AuthUser = Depends(get_current_auth_user),
    user_agent: str = Header(None),
):

    return await regenerate_tokens(
        token=token.refresh_token, user_agent=user_agent, auth_id=current_user.id
    )


@router.put("/change-password", response_model=PasswordChanged)
async def change_password(
    data_obj: ChangePassword,
    current_user: AuthUser = Depends(get_current_auth_user),
    auth_user_service: AuthUserService = Depends(get_auth_user_service),
):
    return await auth_user_service.change_password(
        data_obj=data_obj,
        current_user_password=current_user.password,
        current_user_id=current_user.id,
    )
