from typing import ClassVar, Optional

from pydantic import BaseModel, EmailStr, Field, model_validator

from core.errors import InvalidRequest
from core.schema import Tokens
from schemas.base import ReturnBaseModel, Roles
from utils.email_validation import email_validate
from utils.validate_password import validate_password


class AuthUserCreate(BaseModel):
    PASSWORD: ClassVar[str] = "password"
    EMAIL: ClassVar[str] = "email"

    email: EmailStr
    password: str
    default_role: Roles
    is_superuser: bool = Field(False, hidden_from_schema=True)

    @model_validator(mode="before")
    @classmethod
    def validate_password(cls, values):
        password = values.get(cls.PASSWORD)
        if not validate_password(password):
            raise ValueError(
                "Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one number or one special character"
            )
        return values

    @model_validator(mode="before")
    @classmethod
    def validate_email(cls, values):
        email = values.get(cls.EMAIL)
        if not email_validate(email):
            raise InvalidRequest("Invalid Email Format")

        return values


class AuthUserResponse(ReturnBaseModel):
    ID: ClassVar[str] = "id"

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: EmailStr
    phone_number: Optional[str] = None
    email_verified: Optional[bool] = None
    phone_verified: Optional[bool] = None
    default_role: Roles
    is_superuser: bool = Field(False, hidden_from_schema=True)


class RegisterAuthUserResponse(BaseModel):
    auth_user: AuthUserResponse
    tokens: Tokens


class OtpVerified(BaseModel):
    verified: bool


class LogoutResponse(BaseModel):
    logout: bool = False


class TokenDeactivate(BaseModel):
    access_token: str


class EmailIn(BaseModel):
    email: EmailStr


class NewPassword(BaseModel):
    PASSWORD: ClassVar[str] = "password"
    password: str

    @model_validator(mode="before")
    @classmethod
    def validate_password(cls, values):
        password = values.get(cls.PASSWORD)
        if not validate_password(password):
            raise ValueError(
                "Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one number or one special character"
            )
        return values


class ForgotPassword(BaseModel):
    reset_password_link_sent: bool = True


class ResetPassword(BaseModel):
    password_reset: bool = True


class RefreshTokenSchema(BaseModel):
    refresh_token: str


class ChangePassword(BaseModel):
    NEW_PASSWORD: ClassVar[str] = "new_password"

    old_password: str
    new_password: str

    @model_validator(mode="before")
    @classmethod
    def validate_password(cls, values):
        password = values.get(cls.NEW_PASSWORD)
        if not validate_password(password):
            raise ValueError(
                "Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one number or one special character"
            )
        return values


class PasswordChanged(BaseModel):
    password_changed: bool = True


class UsernameCheck(BaseModel):
    username: str


class UsernameCheckResponse(BaseModel):
    username_exists: bool
