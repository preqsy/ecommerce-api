from typing import Optional
from typing_extensions import Annotated
from pydantic import AnyHttpUrl, BaseModel, Field, StringConstraints


class ProductCreate(BaseModel):
    vendor_id: Optional[int] = None
    product_name: str
    product_image: AnyHttpUrl
    category: str
    short_description: Annotated[str, StringConstraints(max_length=50)]
    sku: str
    product_status: str
    long_description: str
    stock: int
    price: float = Field(gt=0)
