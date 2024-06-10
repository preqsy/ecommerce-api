from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class OTPType(str, Enum):
    PHONE_NUMBER = "phone_number_verification"
    EMAIL = "email_verification"
    RESET_PASSWORD = "reset_password"


class OTPCreate(BaseModel):
    auth_id: int
    token: Optional[str] = None
    otp_type: OTPType
    no_of_trials: Optional[int] = None
