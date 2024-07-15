from fastapi import Depends

from crud import (
    get_crud_auth_user,
    get_crud_refresh_token,
    get_crud_otp,
    get_crud_vendor,
    get_crud_customer,
)
from services import AuthUserService, VendorService, CustomerService
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
