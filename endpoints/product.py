from fastapi import Depends, APIRouter, Query, status

from core.errors import InvalidRequest
from core.tokens import get_current_verified_vendor
from crud.product import CRUDProduct, get_crud_product
from models.auth_user import AuthUser
from schemas import ProductCreate, ProductReturn, ProductUpdate, ProductUpdateReturn
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
    search: str = Query(
        default="", max_length=20, description="Search products with name or category"
    ),
    skip: int = Query(default=0),
    limit: int = Query(default=10),
    crud_product: CRUDProduct = Depends(get_crud_product),
):
    product = crud_product.get_products(search=search, skip=skip, limit=limit)
    if product == []:
        return "No Products"
    return product


@router.get("/me", response_model=list[ProductReturn])
def get_products_vendor(
    search: str = Query(
        default="", max_length=20, description="Search products with name or category"
    ),
    skip: int = Query(default=0),
    limit: int = Query(default=10),
    current_user: AuthUser = Depends(get_current_verified_vendor),
    crud_product: CRUDProduct = Depends(get_crud_product),
):

    product = crud_product.get_products_for_vendor(
        search=search, vendor_id=current_user.role_id, skip=skip, limit=limit
    )
    return product


@router.get("/price")
def sort_product_by_price(
    skip: int = Query(default=0),
    limit: int = Query(default=20),
    crud_product: CRUDProduct = Depends(get_crud_product),
):
    product = crud_product.sort_product_by_price(skip=skip, limit=limit)
    return product


@router.get("/{id}", response_model=ProductReturn)
def get_one_product(
    id: int,
    crud_product: CRUDProduct = Depends(get_crud_product),
):
    product = crud_product.get_or_raise_exception(id)

    return product


@router.put("/{id}", response_model=ProductUpdateReturn)
async def update_product(
    id: int,
    data_obj: ProductUpdate,
    current_user: AuthUser = Depends(get_current_verified_vendor),
    crud_product: CRUDProduct = Depends(get_crud_product),
):

    product = crud_product.get_or_raise_exception(id)
    if product.vendor_id != current_user.role_id:
        raise InvalidRequest("Product doesn't belong to you")

    if data_obj.category:
        data_obj.sku = generate_random_sku(data_obj.category[0:4])

    if data_obj.product_image:
        data_obj.product_image = str(data_obj.product_image)

    updated_product = await crud_product.update(id=id, data_obj=data_obj)

    return updated_product


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    id: int,
    current_user: AuthUser = Depends(get_current_verified_vendor),
    crud_product: CRUDProduct = Depends(get_crud_product),
):
    product = crud_product.get_or_raise_exception(id)
    if product.vendor_id != current_user.role_id:
        raise InvalidRequest("Product doesn't belong to you")
    await crud_product.delete(id)
