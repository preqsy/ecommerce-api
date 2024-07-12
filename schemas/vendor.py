"""Vendor Schema"""

from __future__ import annotations
from typing import Optional
from pydantic import AnyHttpUrl, BaseModel, Field

from schemas.base import CreateBaseModel, CustomerVendorReturnBase
from schemas.order import OrderItemsReturn, OrderReturn


class VendorCreate(CreateBaseModel):
    bio: str
    profile_picture: Optional[AnyHttpUrl] = None
    ratings: Optional[int] = Field(ge=0, le=5)


class VendorReturn(CustomerVendorReturnBase):
    bio: str
    profile_picture: Optional[AnyHttpUrl] = None
    ratings: Optional[int] = None


class TotalSalesReturn(BaseModel):
    total_sales: int
    total_orders: int


class OrdersWithCustomerDetails(OrderItemsReturn):

    order: OrderReturn
