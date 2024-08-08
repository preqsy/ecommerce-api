from pydantic import BaseModel

from schemas.base import Roles


class Tokens(BaseModel):
    access_token: str
    refresh_token: str
    default_role: Roles


class TokenData(BaseModel):
    user_id: int
    user_agent: str


class RefreshTokenCreate(BaseModel):
    auth_id: int
    refresh_token: str
    user_agent: str
    active: bool = True
