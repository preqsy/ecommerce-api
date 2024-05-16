from datetime import datetime
from typing import Optional
from pydantic import BaseModel, constr


class CustomerCreate(BaseModel):
    first_name: constr(min_length=3, to_lower=True)  # type: ignore
    last_name: constr(min_length=3, to_lower=True)  # type: ignore
    username: constr(min_length=3, to_lower=True)  # type: ignore
    phone_number: str  # type: ignore
    auth_id: Optional[int] = None
    country: str
    state: str
    address: str


class CustomerAuthDetails(BaseModel):
    first_name: constr(min_length=3, to_lower=True)  # type: ignore
    last_name: constr(min_length=3, to_lower=True)  # type: ignore
    phone_number: constr(min_length=5, to_lower=True)  # type: ignore
    phone_verified: bool


class CustomerReturn(BaseModel):
    id: int
    first_name: str  # type: ignore
    last_name: str  # type: ignore
    username: str  # type: ignore
    phone_number: str  # type: ignore
    auth_id: Optional[int] = None
    country: str
    state: str
    address: str
    is_superuser: Optional[bool] = None
    created_timestamp: datetime
    updated_timestamp: Optional[datetime] = None
