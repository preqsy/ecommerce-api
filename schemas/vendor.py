from datetime import datetime
from typing import Optional
from typing_extensions import Annotated
from pydantic import AnyHttpUrl, BaseModel, Field, StringConstraints


class VendorCreate(BaseModel):
    first_name: Annotated[str, StringConstraints(min_length=3, to_lower=True)]
    last_name: Annotated[str, StringConstraints(min_length=3, to_lower=True)]
    username: Annotated[str, StringConstraints(min_length=3, to_lower=True)]
    phone_number: str
    auth_id: Optional[int] = None
    country: str
    state: str
    address: str
    bio: str
    profile_picture: Optional[AnyHttpUrl] = None
    ratings: Optional[int] = Field(ge=0, le=5)


class VendorAuthDetails(BaseModel):
    first_name: str
    last_name: str
    phone_number: str


class VendorReturn(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    phone_number: str
    auth_id: Optional[int] = None
    country: str
    state: str
    address: str
    bio: str
    profile_picture: Optional[AnyHttpUrl] = None
    ratings: Optional[int]
    is_superuser: Optional[bool] = None
    created_timestamp: datetime
    updated_timestamp: Optional[datetime] = None
