from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from schemas.base import PaymentType, ReturnBaseModel
from schemas.customer import CustomerReturn
from schemas.product import ProductReturn


class CartCreate(BaseModel):
    product_id: int
    customer_id: Optional[int] = None
    cart_id: Optional[str] = None
    quantity: int = Field(default=1)


class CartUpdate(BaseModel):
    product_id: int
    quantity: int


class CartReturn(ReturnBaseModel):
    product_id: int
    quantity: int
    customer_id: int
    total_amount: Optional[float] = None
    product: ProductReturn
    customer: CustomerReturn


class CartTotalAmount(CartReturn):
    cart_items: List[CartReturn]
    total_amount: float


class CartSummary(BaseModel):
    total_items_quantity: int
    total_amount: float
    cart_items: List[CartReturn]


class CartUpdateReturn(BaseModel):
    product_id: int
    quantity: int
    updated_timestamp: datetime


class OrderCreate(BaseModel):
    payment_type: PaymentType
    shipping_address: Optional[str] = None
    additional_note: Optional[str] = None
    contact_information: Optional[str] = None
    customer_id: Optional[int] = None
    vendor_ids: Optional[list] = []
    total_amount: Optional[float] = None
