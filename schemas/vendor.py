"""Vendor Schema"""

from typing import Optional
from pydantic import AnyHttpUrl, Field

from schemas.base import CreateBaseModel, ReturnBaseModel


class VendorCreate(CreateBaseModel):
    bio: str
    profile_picture: Optional[AnyHttpUrl] = None
    ratings: Optional[int] = Field(ge=0, le=5)


class VendorReturn(ReturnBaseModel):

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
