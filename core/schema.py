from pydantic import BaseModel


class Tokens(BaseModel):
    access_token: str
    refresh_token: str


class TokenData(BaseModel):
    user_id: int
    user_agent: str


class RefreshTokenCreate(BaseModel):
    auth_id: int
    refresh_token: str
    user_agent: str
    active: bool = False
