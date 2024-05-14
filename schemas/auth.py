from datetime import datetime
from enum import Enum
from typing import ClassVar, Optional
from pydantic import BaseModel, EmailStr, Field
from core.schema import Token


class Roles(str, Enum):
    CUSTOMER = "customer"
    VENDOR = "vendor"


class AuthUserCreate(BaseModel):
    email: EmailStr
    password: str
    default_role: Roles
    is_superuser: bool = Field(False, hidden_from_schema=True)


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
