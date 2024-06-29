from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from schemas.base import PaymentMethodEnum, StatusEnum


class OrderCreate(BaseModel):
    customer_id: Optional[int] = None
    status: StatusEnum = StatusEnum.PROCESSING
    total_amount: Optional[float] = None


class OrderItemsCreate(BaseModel):
    order_id: Optional[int] = None
    vendor_id: Optional[int] = None
    product_id: Optional[int] = None
    price: Optional[int] = None
    quantity: Optional[int] = None


class PaymentDetailsCreate(BaseModel):
    order_id: Optional[int] = None
    payment_method: PaymentMethodEnum
    amount: Optional[int] = None
    status: StatusEnum = StatusEnum.PROCESSING
    payment_ref: Optional[str] = None


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
