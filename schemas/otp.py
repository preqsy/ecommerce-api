from enum import Enum
from typing import Optional
from pydantic import BaseModel


class OTPType(str, Enum):
    PHONE_NUMBER = "phone_number_verification"
    EMAIL = "email_verification"


class OTPCreate(BaseModel):
    auth_id: int
    token: Optional[str] = None
    otp_type: OTPType
