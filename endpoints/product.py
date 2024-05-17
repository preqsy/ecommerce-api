from typing import Optional
from fastapi import Depends, APIRouter, Query, status, UploadFile

from core.tokens import get_current_verified_customer, get_current_verified_vendor
from crud.product import CRUDProduct, get_crud_product
from models.auth_user import AuthUser
from schemas import ProductCreate, ProductReturn
from utils.generate_sku import generate_random_sku

router = APIRouter(prefix="/products", tags=["Product"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ProductReturn)
async def create_product(
    data_obj: ProductCreate,
    current_user: AuthUser = Depends(get_current_verified_vendor),
    crud_product: CRUDProduct = Depends(get_crud_product),
):
    data_obj.vendor_id = current_user.role_id
    data_obj.sku = generate_random_sku(data_obj.category[0:4])
    data_obj.product_image = str(data_obj.product_image)
    product = await crud_product.create(data_obj)

    return product


@router.get("", response_model=list[ProductReturn])
def get_products_customer(
    search: str = Query(default=""),
    crud_product: CRUDProduct = Depends(get_crud_product),
):
    product = crud_product.get_products(search=search)
    if product == []:
        return "No Products"
    return product
