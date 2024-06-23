from arq import ArqRedis
from fastapi import Depends, APIRouter, Query, status

from core.errors import InvalidRequest, MissingResources
from core.tokens import get_current_verified_vendor
from crud import (
    CRUDProduct,
    CRUDProductCategory,
    CRUDProductImage,
    get_crud_product,
    get_crud_product_category,
    get_crud_product_image,
)
from models import AuthUser, ProductCategory
from schemas import (
    ProductCreate,
    ProductReturn,
    ProductUpdate,
    ProductUpdateReturn,
    ProductImageUpdate,
    ProductImageUpdateReturn,
)
from task_queue.main import get_queue_connection
from utils.generate_sku import generate_random_sku

router = APIRouter(prefix="/products", tags=["Product"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ProductReturn)
async def create_product(
    data_obj: ProductCreate,
    current_user: AuthUser = Depends(get_current_verified_vendor),
    crud_product: CRUDProduct = Depends(get_crud_product),
    crud_product_category: CRUDProductCategory = Depends(get_crud_product_category),
    queue_connection: ArqRedis = Depends(get_queue_connection),
):
    category = crud_product_category.get_by_category_name(
        category_name=data_obj.category
    )
    if not category:
        new_category = await crud_product_category.create(
            data_obj={ProductCategory.CATEGORY_NAME: data_obj.category}
        )
        data_obj.product_category_id = new_category.id
    else:
        data_obj.product_category_id = category.id
    data_obj.vendor_id = current_user.role_id
    data_obj.sku = generate_random_sku(data_obj.category[0:4])
    del data_obj.category
    product_images = data_obj.product_images
    del data_obj.product_images

    product = await crud_product.create(data_obj)
    await queue_connection.enqueue_job(
        "save_product_images", product.id, product_images
    )
    return product


@router.get("", response_model=list[ProductReturn])
def get_products_customer(
    search: str = Query(
        default="", max_length=20, description="Search products with name or category"
    ),
    skip: int = Query(default=0),
    limit: int = Query(default=20),
    crud_product: CRUDProduct = Depends(get_crud_product),
):
    products = crud_product.get_products(search=search, skip=skip, limit=limit)
    if not products:
        raise MissingResources("No Products")
    return products


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


@router.get("/price", response_model=list[ProductReturn])
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
    crud_product_category: CRUDProductCategory = Depends(get_crud_product_category),
):

    product = crud_product.get_or_raise_exception(id)
    if product.vendor_id != current_user.role_id:
        raise InvalidRequest("Product doesn't belong to you")

    if data_obj.category:
        data_obj.sku = generate_random_sku(data_obj.category[0:4])
        prod_cat = await crud_product_category.create(
            data_obj={ProductCategory.CATEGORY_NAME: data_obj.category}
        )
        data_obj.product_category_id = prod_cat.id

    del data_obj.category

    updated_product = await crud_product.update(id=id, data_obj=data_obj)

    return updated_product


@router.put("/image/{product_image_id}", response_model=ProductImageUpdateReturn)
async def update_product_image(
    product_image_id: int,
    data_obj: ProductImageUpdate,
    current_user: AuthUser = Depends(get_current_verified_vendor),
    crud_product_image: CRUDProductImage = Depends(get_crud_product_image),
    crud_product: CRUDProduct = Depends(get_crud_product),
):

    product_image = crud_product_image.get_or_raise_exception(product_image_id)
    product = crud_product.get_or_raise_exception(id=product_image.product_id)
    if product.vendor_id != current_user.role_id:
        raise InvalidRequest("Product doesn't belong to you")
    data_obj.product_image = str(data_obj.product_image)

    updated_product_image = await crud_product_image.update(
        id=product_image_id, data_obj=data_obj
    )

    return updated_product_image


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
