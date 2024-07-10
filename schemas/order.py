from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from schemas.base import PaymentMethodEnum, ReturnBaseModel, StatusEnum
from schemas import CustomerReturn


class OrderCreate(BaseModel):
    customer_id: Optional[int] = None
    status: StatusEnum = StatusEnum.PROCESSING
    total_amount: Optional[float] = None


class OrderReturn(ReturnBaseModel):
    customer_id: Optional[int] = None
    status: StatusEnum = StatusEnum.PROCESSING
    total_amount: Optional[float] = None
    order_date: Optional[datetime] = None
    customer: CustomerReturn


class OrderItemsCreate(BaseModel):
    order_id: int
    vendor_id: int
    product_id: int
    price: int
    quantity: int


class OrderItemsReturn(ReturnBaseModel, OrderItemsCreate):
    "Return Schema for Items In an Order"


class PaymentDetailsCreate(BaseModel):
    order_id: Optional[int] = None
    payment_method: PaymentMethodEnum
    amount: Optional[int] = None
    status: StatusEnum = StatusEnum.PROCESSING
    payment_ref: Optional[str] = None
    paid_at: Optional[datetime] = None


class ShippingDetailsCreate(BaseModel):
    order_id: Optional[int] = None
    address: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    additional_note: Optional[str] = None
    contact_information: Optional[str] = None
    shipping_date: Optional[datetime] = None


class CheckoutCreate(BaseModel):
    payment_details: PaymentDetailsCreate
    shipping_details: Optional[ShippingDetailsCreate] = None


class PaymentVerified(BaseModel):
    payment_verified: bool = True
