from datetime import datetime
from typing import Annotated, Optional
from pydantic import BaseModel, Field, StringConstraints, constr


class CustomerCreate(BaseModel):
    first_name: Annotated[str, StringConstraints(min_length=3, to_lower=True)]
    last_name: Annotated[str, StringConstraints(min_length=3, to_lower=True)]
    username: Annotated[str, StringConstraints(min_length=3, to_lower=True)]
    phone_number: str
    auth_id: Optional[int] = None
    country: str
    state: str
    address: str


class CustomerAuthDetails(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    role_id: int


class CustomerReturn(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    phone_number: str
    auth_id: Optional[int] = None
    country: str
    state: str
    address: str
    is_superuser: Optional[bool] = None
    created_timestamp: datetime
    updated_timestamp: Optional[datetime] = None
