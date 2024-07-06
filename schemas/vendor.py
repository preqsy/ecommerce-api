"""Vendor Schema"""

from typing import Optional
from pydantic import AnyHttpUrl, Field, BaseModel

from schemas.base import CreateBaseModel, CustomerVendorReturnBase


class VendorCreate(CreateBaseModel):
    bio: str
    profile_picture: Optional[AnyHttpUrl] = None
    ratings: Optional[int] = Field(ge=0, le=5)


class VendorReturn(CustomerVendorReturnBase):

    profile_picture: Optional[AnyHttpUrl] = None
    ratings: Optional[int]


class VendorDashboardReturn(BaseModel):
    total_sales: int
    total_orders: int


class TotalSalesReturn(BaseModel):
    total_sales: int
