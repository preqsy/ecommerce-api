from datetime import datetime
from typing import ClassVar, Optional
from typing_extensions import Annotated
from pydantic import AnyHttpUrl, BaseModel, Field, StringConstraints

from schemas.base import ProductCategoryEnum, ProductOptionalBase, ReturnBaseModel


class ProductImageCreate(BaseModel):
    product_image: str
    product_id: int


class ProductCategoryCreate(BaseModel):
    category_name: ProductCategoryEnum


class ProductImageReturn(ReturnBaseModel):
    product_image: str
    product_id: int


class ProductCategoryReturn(ReturnBaseModel):
    category_name: ProductCategoryEnum


class ProductCreate(ProductOptionalBase):
    PRODUCT_STATUS: ClassVar[str] = "product_status"

    vendor_id: Optional[int] = None
    product_name: str
    product_images: list[AnyHttpUrl]
    category: ProductCategoryEnum
    short_description: Annotated[str, StringConstraints(max_length=50)]
    product_status: bool = True
    long_description: str
    stock: int
    price: float = Field(gt=0)


class ProductReturn(ReturnBaseModel, ProductCreate):
    CREATED_TIMESTAMP: ClassVar[str] = "created_timestamp"

    product_images: list[ProductImageReturn]
    category: ProductCategoryReturn


class ProductUpdate(ProductOptionalBase):
    product_name: Optional[str] = None
    short_description: Optional[str] = None
    category: Optional[ProductCategoryEnum] = None
    product_status: Optional[bool] = None
    long_description: Optional[str] = None
    stock: Optional[int] = None
    price: Optional[float] = None


class ProductImageUpdate(BaseModel):
    product_image: AnyHttpUrl


class ProductImageUpdateReturn(ProductImageUpdate):
    updated_timestamp: datetime


class ProductUpdateReturn(ProductUpdate):
    created_timestamp: Optional[datetime] = None
    updated_timestamp: Optional[datetime] = None
