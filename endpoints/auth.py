from fastapi import APIRouter, Depends, BackgroundTasks, Header, Query, status
from fastapi.security import OAuth2PasswordRequestForm

from core.errors import InvalidRequest, MissingResources, ResourcesExist
from core.schema import RefreshTokenCreate, Tokens
from core.tokens import (
    create_forget_password_token,
    deactivate_token,
    generate_tokens,
    get_current_auth_user,
    regenerate_tokens,
    verify_access_token,
)
from crud import (
    CRUDAuthUser,
    CRUDRefreshToken,
    CRUDOtp,
    get_crud_auth_user,
    get_crud_refresh_token,
    get_crud_otp,
)

from schemas import (
    AuthUserCreate,
    AuthUserResponse,
    LogoutResponse,
    RegisterAuthUserResponse,
    TokenDeactivate,
    OtpVerified,
    OTPCreate,
    OTPType,
    NewPassword,
    EmailIn,
    ForgotPassword,
    ResetPassword,
    RefreshTokenSchema,
    ChangePassword,
    PasswordChanged,
)
from models import OTP, AuthUser
from utils.email_validation import email_validate
from utils.password_utils import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=RegisterAuthUserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    data_obj: AuthUserCreate,
    background_task: BackgroundTasks,
    crud_auth_user: CRUDAuthUser = Depends(get_crud_auth_user),
    crud_refresh_token: CRUDRefreshToken = Depends(get_crud_refresh_token),
    crud_otp: CRUDOtp = Depends(get_crud_otp),
    user_agent: str = Header(None),
):
    data_obj.email = data_obj.email.lower()
    if not email_validate(data_obj.email):
        raise InvalidRequest("Invalid Email")
    email = crud_auth_user.get_by_email(data_obj.email)
    if email:
        raise ResourcesExist("Email Exists")
    data_obj.password = hash_password(data_obj.password)
    new_user = await crud_auth_user.create(data_obj)
    otp_data_obj = OTPCreate(auth_id=new_user.id, otp_type=OTPType.EMAIL)
    background_task.add_task(crud_otp.create, otp_data_obj)
    tokens = generate_tokens(user_id=new_user.id, user_agent=user_agent)
    token_obj = RefreshTokenCreate(
        auth_id=new_user.id, refresh_token=tokens.refresh_token, user_agent=user_agent
    )
    await crud_refresh_token.create(data_obj=token_obj)

    new_user_dict = data_obj.model_dump()
    new_user_dict[AuthUserResponse.ID] = new_user.id
    return RegisterAuthUserResponse(auth_user=new_user_dict, tokens=tokens)


@router.post("/verify", response_model=OtpVerified)
async def verify(
    data_obj: OTPCreate,
    crud_auth_user: CRUDAuthUser = Depends(get_crud_auth_user),
    crud_otp: CRUDOtp = Depends(get_crud_otp),
):
    crud_auth_user.get_or_raise_exception(id=data_obj.auth_id)
    otp_verify: OTP = await crud_otp.verify_otp(
        auth_id=data_obj.auth_id, token=data_obj.token, otp_type=data_obj.otp_type
    )
    if not otp_verify:
        raise InvalidRequest("Invalid OTP")
    if data_obj.otp_type == OTPType.EMAIL:
        await crud_auth_user.update(
            id=data_obj.auth_id, data_obj={AuthUser.EMAIL_VERIFIED: True}
        )
    if data_obj.otp_type == OTPType.PHONE_NUMBER:
        await crud_auth_user.update(
            id=data_obj.auth_id, data_obj={AuthUser.PHONE_VERIFIED: True}
        )
    return OtpVerified(verified=True)


@router.post("/token", status_code=status.HTTP_201_CREATED, response_model=Tokens)
async def login_user(
    data_obj: OAuth2PasswordRequestForm = Depends(),
    crud_auth_user: CRUDAuthUser = Depends(get_crud_auth_user),
    crud_refresh_token: CRUDRefreshToken = Depends(get_crud_refresh_token),
    user_agent: str = Header(None),
):
    user_query = crud_auth_user.get_by_email(email=data_obj.username.lower())
    if not user_query:
        raise InvalidRequest("Incorrect Credentials")

    if not user_query.email_verified:
        raise InvalidRequest("Unverfied Email")

    if not verify_password(
        plain_password=data_obj.password, hashed_password=user_query.password
    ):
        raise InvalidRequest("Incorrect Credentials")
    tokens = generate_tokens(user_id=user_query.id, user_agent=user_agent)
    token_obj = RefreshTokenCreate(
        refresh_token=tokens.refresh_token,
        auth_id=user_query.id,
        user_agent=user_agent,
    )
    await crud_refresh_token.create(data_obj=token_obj)
    return tokens


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
    background_task: BackgroundTasks,
    user_agent: str = Header(None),
    crud_auth_user: CRUDAuthUser = Depends(get_crud_auth_user),
    crud_otp: CRUDOtp = Depends(get_crud_otp),
):
    user_query = crud_auth_user.get_by_email(data_obj.email.lower())
    if not user_query:
        raise MissingResources()
    otp_query = await crud_otp.check_number_of_trials(user_query.id)

    if otp_query and otp_query.no_of_tries >= 3:
        raise InvalidRequest("Max Limit Reached")

    OTP_QUERY_COUNT = otp_query.no_of_tries if otp_query else 0

    token = create_forget_password_token(auth_id=user_query.id, user_agent=user_agent)

    otp_obj = OTPCreate(
        auth_id=user_query.id, otp_type=OTPType.RESET_PASSWORD, token=token
    )
    background_task.add_task(crud_otp.create, otp_obj, OTP_QUERY_COUNT)

    return ForgotPassword()


@router.post("/reset-password", response_model=ResetPassword)
async def reset_password(
    data_obj: NewPassword,
    token: str = Query(),
    crud_auth_user: CRUDAuthUser = Depends(get_crud_auth_user),
    crud_otp: CRUDOtp = Depends(get_crud_otp),
):

    token_data = verify_access_token(token)
    user_query = crud_auth_user.get_or_raise_exception(id=token_data.user_id)
    if verify_password(data_obj.password, hashed_password=user_query.password):
        raise InvalidRequest("Can't change password to old password")
    data_obj.password = hash_password(data_obj.password)
    await crud_auth_user.update(id=token_data.user_id, data_obj=data_obj)
    deactivate_token(token)
    await crud_otp.delete_by_auth_id(auth_id=token_data.user_id)

    return ResetPassword()


@router.get("/me", response_model=AuthUserResponse)
def get_me(
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
    crud_auth_user: CRUDAuthUser = Depends(get_crud_auth_user),
):
    if not verify_password(
        plain_password=data_obj.old_password, hashed_password=current_user.password
    ):
        raise InvalidRequest("Wrong password")

    if verify_password(
        plain_password=data_obj.new_password, hashed_password=current_user.password
    ):
        raise InvalidRequest("Cannot change to old password")

    await crud_auth_user.update(
        id=current_user.id,
        data_obj={AuthUser.PASSWORD: hash_password(data_obj.new_password)},
    )
    return PasswordChanged()
