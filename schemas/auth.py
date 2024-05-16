from datetime import datetime
from enum import Enum
from typing import ClassVar, Optional
from pydantic import BaseModel, EmailStr, Field, model_validator, root_validator
from core.schema import Token
from utils.validate_password import validate_password


class Roles(str, Enum):
    CUSTOMER = "customer"
    VENDOR = "vendor"


class AuthUserCreate(BaseModel):
    PASSWORD: ClassVar[str] = "password"
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


class AuthUserResponse(BaseModel):
    ID: ClassVar[str] = "id"
    id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: EmailStr = None
    phone_number: Optional[str] = None
    email_verified: Optional[bool] = None
    phone_verified: Optional[bool] = None
    default_role: Roles = None
    is_superuser: bool = Field(False, hidden_from_schema=True)
    created_timestamp: Optional[datetime] = None
    updated_timestamp: Optional[datetime] = None


class RegisterAuthUserResponse(BaseModel):
    auth_user: AuthUserResponse
    tokens: Token


class AuthUserUpdate(BaseModel):
    email: EmailStr


class VerifiedEmail(BaseModel):
    email_verified: bool
