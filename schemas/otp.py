from pydantic import BaseModel


class OTPCreate(BaseModel):
    token: str
    auth_id: int
