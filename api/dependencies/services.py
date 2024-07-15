from fastapi import Depends

from core.paystack import get_paystack
from crud import (
    get_crud_auth_user,
    get_crud_refresh_token,
    get_crud_otp,
    get_crud_vendor,
    get_crud_customer,
    get_crud_product,
    get_crud_product_category,
    get_crud_product_image,
    get_crud_product_review,
    get_crud_cart,
    get_crud_payment_details,
    get_crud_order_item,
    get_crud_order,
)
from services import (
    AuthUserService,
    VendorService,
    CustomerService,
    ProductService,
    CartService,
    OrderService,
)
from task_queue.main import get_queue_connection


def get_auth_user_service(
    crud_auth_user=Depends(get_crud_auth_user),
    crud_refresh_token=Depends(get_crud_refresh_token),
    crud_otp=Depends(get_crud_otp),
) -> AuthUserService:
    return AuthUserService(
        crud_auth_user=crud_auth_user,
        crud_refresh_token=crud_refresh_token,
        crud_otp=crud_otp,
    )


def get_customer_service(
    crud_auth_user=Depends(get_crud_auth_user),
    crud_otp=Depends(get_crud_otp),
    crud_customer=Depends(get_crud_customer),
    queue_connection=Depends(get_queue_connection),
) -> CustomerService:
    return CustomerService(
        crud_auth_user=crud_auth_user,
        crud_otp=crud_otp,
        crud_customer=crud_customer,
        queue_connection=queue_connection,
    )


def get_vendor_service(
    crud_auth_user=Depends(get_crud_auth_user),
    crud_otp=Depends(get_crud_otp),
    crud_vendor=Depends(get_crud_vendor),
    queue_connection=Depends(get_queue_connection),
) -> VendorService:
    return VendorService(
        crud_auth_user=crud_auth_user,
        crud_otp=crud_otp,
        crud_vendor=crud_vendor,
        queue_connection=queue_connection,
    )


def get_product_service(
    crud_auth_user=Depends(get_crud_auth_user),
    queue_connection=Depends(get_queue_connection),
    crud_product=Depends(get_crud_product),
    crud_product_category=Depends(get_crud_product_category),
    crud_product_image=Depends(get_crud_product_image),
    crud_product_review=Depends(get_crud_product_review),
) -> ProductService:
    return ProductService(
        crud_auth_user=crud_auth_user,
        queue_connection=queue_connection,
        crud_product_category=crud_product_category,
        crud_product=crud_product,
        crud_product_image=crud_product_image,
        crud_product_review=crud_product_review,
    )


def get_cart_service(
    crud_auth_user=Depends(get_crud_auth_user),
    queue_connection=Depends(get_queue_connection),
    crud_product=Depends(get_crud_product),
    crud_cart=Depends(get_crud_cart),
    crud_customer=Depends(get_crud_customer),
    crud_order=Depends(get_crud_order),
    crud_payment=Depends(get_crud_payment_details),
    paystack=Depends(get_paystack),
) -> CartService:
    return CartService(
        crud_auth_user=crud_auth_user,
        queue_connection=queue_connection,
        crud_product=crud_product,
        crud_cart=crud_cart,
        crud_customer=crud_customer,
        crud_order=crud_order,
        crud_payment=crud_payment,
        paystack=paystack,
    )


def get_order_service(
    crud_customer=Depends(get_crud_customer),
    crud_order=Depends(get_crud_order),
    crud_order_item=Depends(get_crud_order_item),
) -> OrderService:
    return OrderService(
        crud_customer=crud_customer,
        crud_order=crud_order,
        crud_order_item=crud_order_item,
    )
