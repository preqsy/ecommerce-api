from fastapi import BackgroundTasks, Header
from fastapi.security import OAuth2PasswordRequestForm

from core.errors import InvalidRequest, MissingResources, ResourcesExist
from core.schema import RefreshTokenCreate
from core.tokens import (
    create_forget_password_token,
    deactivate_token,
    generate_tokens,
    verify_access_token,
)
from crud import CRUDAuthUser, CRUDRefreshToken, CRUDOtp
from models.auth_user import AuthUser
from schemas import (
    AuthUserCreate,
    AuthUserResponse,
    RegisterAuthUserResponse,
    OTPCreate,
    OTPType,
    OtpVerified,
    ChangePassword,
    EmailIn,
    ForgotPassword,
    NewPassword,
    PasswordChanged,
    ResetPassword,
)
from utils.password_utils import hash_password, verify_password


class AuthUserService:

    def __init__(
        self,
        crud_auth_user: CRUDAuthUser,
        crud_refresh_token: CRUDRefreshToken,
        crud_otp: CRUDOtp,
    ):
        self.crud_auth_user = crud_auth_user
        self.crud_refresh_token = crud_refresh_token
        self.crud_otp = crud_otp

    async def register_auth_user(
        self,
        data_obj: AuthUserCreate,
        background_task: BackgroundTasks,
        user_agent: str = Header(None),
    ):
        data_obj.email = data_obj.email.lower()
        email = self.crud_auth_user.get_by_email(data_obj.email)
        if email:
            raise ResourcesExist("Email Exists")
        data_obj.password = hash_password(data_obj.password)
        new_user = await self.crud_auth_user.create(data_obj)
        otp_data_obj = OTPCreate(auth_id=new_user.id, otp_type=OTPType.EMAIL)
        background_task.add_task(self.crud_otp.create, otp_data_obj)
        tokens = generate_tokens(user_id=new_user.id, user_agent=user_agent)
        token_obj = RefreshTokenCreate(
            auth_id=new_user.id,
            refresh_token=tokens.refresh_token,
            user_agent=user_agent,
        )
        await self.crud_refresh_token.create(data_obj=token_obj)

        new_user_dict = data_obj.model_dump()
        new_user_dict[AuthUserResponse.ID] = new_user.id
        return RegisterAuthUserResponse(auth_user=new_user_dict, tokens=tokens)

    async def login_user(
        self,
        form_data: OAuth2PasswordRequestForm,
        user_agent: str = Header(None),
    ):
        user_query = self.crud_auth_user.get_by_email(email=form_data.username.lower())
        if not user_query:
            raise InvalidRequest("Incorrect Credentials")

        if not user_query.email_verified:
            raise InvalidRequest("Unverfied Email")

        if not verify_password(
            plain_password=form_data.password, hashed_password=user_query.password
        ):
            raise InvalidRequest("Incorrect Credentials")
        tokens = generate_tokens(user_id=user_query.id, user_agent=user_agent)
        token_obj = RefreshTokenCreate(
            refresh_token=tokens.refresh_token,
            auth_id=user_query.id,
            user_agent=user_agent,
        )
        await self.crud_refresh_token.create(data_obj=token_obj)
        return tokens

    async def verify(
        self,
        data_obj: OTPCreate,
    ):
        self.crud_auth_user.get_or_raise_exception(id=data_obj.auth_id)
        otp_verify = await self.crud_otp.verify_otp(
            auth_id=data_obj.auth_id, token=data_obj.token, otp_type=data_obj.otp_type
        )
        if not otp_verify:
            raise InvalidRequest("Invalid OTP")
        if data_obj.otp_type == OTPType.EMAIL:
            await self.crud_auth_user.update(
                id=data_obj.auth_id, data_obj={AuthUser.EMAIL_VERIFIED: True}
            )
        if data_obj.otp_type == OTPType.PHONE_NUMBER:
            await self.crud_auth_user.update(
                id=data_obj.auth_id, data_obj={AuthUser.PHONE_VERIFIED: True}
            )
        return OtpVerified(verified=True)

    async def forget_password(
        self,
        data_obj: EmailIn,
        user_agent: str,
        background_tasks: BackgroundTasks,
    ):
        user_query = self.crud_auth_user.get_by_email(data_obj.email.lower())
        if not user_query:
            raise MissingResources()
        otp_query = await self.crud_otp.check_number_of_trials(user_query.id)

        if otp_query and otp_query.no_of_tries >= 3:
            raise InvalidRequest("Max Limit Reached")

        OTP_QUERY_COUNT = otp_query.no_of_tries if otp_query else 0

        token = create_forget_password_token(
            auth_id=user_query.id, user_agent=user_agent
        )

        otp_obj = OTPCreate(
            auth_id=user_query.id, otp_type=OTPType.RESET_PASSWORD, token=token
        )
        background_tasks.add_task(self.crud_otp.create, otp_obj, OTP_QUERY_COUNT)

        return ForgotPassword()

    async def reset_password(self, data_obj: NewPassword, token: str):

        token_data = verify_access_token(token)
        user_query = self.crud_auth_user.get_or_raise_exception(id=token_data.user_id)
        if verify_password(data_obj.password, hashed_password=user_query.password):
            raise InvalidRequest("Can't change password to old password")
        data_obj.password = hash_password(data_obj.password)
        await self.crud_auth_user.update(id=token_data.user_id, data_obj=data_obj)
        deactivate_token(auth_id=user_query.id, token=token)
        await self.crud_otp.delete_by_auth_id(auth_id=token_data.user_id)

        return ResetPassword()

    async def change_password(
        self, data_obj: ChangePassword, current_user_id: int, current_user_password: str
    ):
        if not verify_password(
            plain_password=data_obj.old_password, hashed_password=current_user_password
        ):
            raise InvalidRequest("Wrong old password")

        if verify_password(
            plain_password=data_obj.new_password, hashed_password=current_user_password
        ):
            raise InvalidRequest("Cannot change to old password")

        await self.crud_auth_user.update(
            id=current_user_id,
            data_obj={AuthUser.PASSWORD: hash_password(data_obj.new_password)},
        )

        return PasswordChanged()
