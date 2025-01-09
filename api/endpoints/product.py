from fastapi import Depends, APIRouter, Query, status

from api.dependencies.services import get_product_service
from core.tokens import get_current_verified_customer, get_current_verified_vendor
from models import AuthUser
from schemas import (
    ProductCreate,
    ProductReturn,
    ProductUpdate,
    ProductUpdateReturn,
    ProductImageUpdate,
    ProductImageUpdateReturn,
    ProductReviewCreate,
    ProductsReturn,
    ProductReviewReturn,
    ProductReviewUpdate,
    ProductReviewUpdateReturn,
)
from services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["Product"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ProductReturn,
)
async def create_product(
    data_obj: ProductCreate,
    current_user: AuthUser = Depends(get_current_verified_vendor),
    product_service: ProductService = Depends(get_product_service),
):

    return await product_service.create_product(
        data_obj=data_obj, current_user=current_user
    )


@router.get("", response_model=list[ProductsReturn])
async def get_products_customer(
    search: str = Query(
        default="", max_length=20, description="Search products with name or category"
    ),
    skip: int = Query(default=0),
    limit: int = Query(default=20),
    product_service: ProductService = Depends(get_product_service),
):

    return await product_service.get_products_customer(
        search=search, skip=skip, limit=limit
    )


@router.get("/me", response_model=list[ProductReturn])
async def get_products_vendor(
    search: str = Query(
        default="", max_length=20, description="Search products with name or category"
    ),
    skip: int = Query(default=0),
    limit: int = Query(default=10),
    current_user: AuthUser = Depends(get_current_verified_vendor),
    product_service: ProductService = Depends(get_product_service),
):

    return await product_service.get_products_vendor(
        search=search, skip=skip, limit=limit, vendor_id=current_user.role_id
    )


@router.get("/price", response_model=list[ProductReturn])
async def sort_product_by_price(
    skip: int = Query(default=0),
    limit: int = Query(default=20),
    product_service: ProductService = Depends(get_product_service),
):
    return await product_service.sort_product_by_price(
        skip=skip,
        limit=limit,
    )


@router.get("/{id}", response_model=ProductReturn)
async def get_one_product(
    id: int,
    product_service: ProductService = Depends(get_product_service),
):
    return await product_service.get_one_product(product_id=id)


@router.put("/{id}", response_model=ProductUpdateReturn)
async def update_product(
    id: int,
    data_obj: ProductUpdate,
    current_user: AuthUser = Depends(get_current_verified_vendor),
    product_service: ProductService = Depends(get_product_service),
):

    return await product_service.update_product(
        product_id=id, vendor_id=current_user.role_id, data_obj=data_obj
    )


@router.put("/image/{product_image_id}", response_model=ProductImageUpdateReturn)
async def update_product_image(
    product_image_id: int,
    data_obj: ProductImageUpdate,
    current_user: AuthUser = Depends(get_current_verified_vendor),
    product_service: ProductService = Depends(get_product_service),
):

    return await product_service.update_product_image(
        product_image_id=product_image_id,
        vendor_id=current_user.role_id,
        data_obj=data_obj,
    )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    id: int,
    current_user: AuthUser = Depends(get_current_verified_vendor),
    product_service: ProductService = Depends(get_product_service),
):

    return await product_service.delete_product(
        product_id=id, vendor_id=current_user.role_id
    )


@router.post(
    "/add-review",
    status_code=status.HTTP_201_CREATED,
    response_model=ProductReviewReturn,
)
async def create_product_review(
    data_obj: ProductReviewCreate,
    current_user: AuthUser = Depends(get_current_verified_customer),
    product_service: ProductService = Depends(get_product_service),
):

    return await product_service.create_product_review(data_obj)


@router.put(
    "/edit-review/{review_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=ProductReviewUpdateReturn,
)
async def update_product_review(
    review_id: int,
    data_obj: ProductReviewUpdate,
    current_user: AuthUser = Depends(get_current_verified_customer),
    product_service: ProductService = Depends(get_product_service),
):

    return await product_service.update_product_review(
        review_id=review_id, data_obj=data_obj
    )
