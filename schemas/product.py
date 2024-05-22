from datetime import datetime
from typing import Any, ClassVar, List, Optional
from typing_extensions import Annotated
from pydantic import AnyHttpUrl, BaseModel, Field, StringConstraints

from models.cart import Cart
from schemas.base import ProductCategory, ReturnBaseModel
from schemas.customer import CustomerReturn


class ProductCreate(BaseModel):
    PRODUCT_STATUS: ClassVar[str] = "product_status"

    vendor_id: Optional[int] = None
    product_name: str
    product_image: AnyHttpUrl
    category: ProductCategory
    short_description: Annotated[str, StringConstraints(max_length=50)]
    sku: Optional[str] = None
    product_status: bool = True
    long_description: str
    stock: int
    price: float = Field(gt=0)


class ProductReturn(ReturnBaseModel):
    CREATED_TIMESTAMP: ClassVar[str] = "created_timestamp"

    vendor_id: int
    product_name: str
    product_image: AnyHttpUrl
    category: str
    short_description: str
    sku: str
    product_status: bool
    long_description: str
    stock: int
    price: float


class ProductUpdate(BaseModel):
    product_name: Optional[str] = None
    product_image: Optional[AnyHttpUrl] = None
    category: Optional[str] = None
    short_description: Optional[str] = None
    sku: Optional[str] = None
    product_status: Optional[bool] = None
    long_description: Optional[str] = None
    stock: Optional[int] = None
    price: Optional[float] = None


class ProductUpdateReturn(ProductUpdate):
    created_timestamp: Optional[datetime] = None
    updated_timestamp: Optional[datetime] = None


class CartCreate(BaseModel):
    product_id: int
    customer_id: Optional[int] = None
    session: Optional[int] = None
    quantity: int = Field(default=1)


class CartUpdate(BaseModel):

    quantity: int = Field(default=1)


class CartReturn(ReturnBaseModel):
    product_id: int
    quantity: int
    customer_id: int
    total_amount: Optional[int] = None
    product: ProductReturn
    customer: CustomerReturn


class CartTotalAmount(CartReturn):
    # cart: list
    cart_items: List[CartReturn]
    total_amount: float
