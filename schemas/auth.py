from enum import Enum
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
    auth_user: AuthUserCreate
    tokens: Token
