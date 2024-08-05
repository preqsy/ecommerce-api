from fastapi import APIRouter, Depends, status

from api.dependencies.services import get_cart_service
from core.tokens import (
    get_current_verified_customer,
)
from models import AuthUser
from schemas import (
    CartCreate,
    CartReturn,
    CartUpdate,
    CartUpdateReturn,
    CartSummary,
    CheckoutCreate,
    PaymentVerified,
)
from services.cart_service import CartService


router = APIRouter(prefix="/cart", tags=["Cart"])


@router.post("/add", status_code=status.HTTP_201_CREATED, response_model=CartReturn)
async def create_cart(
    data_obj: CartCreate,
    cart_service: CartService = Depends(get_cart_service),
    current_user: AuthUser = Depends(get_current_verified_customer),
):
    return await cart_service.create_cart(
        data_obj=data_obj, customer_id=current_user.role_id
    )


@router.put("/", response_model=CartUpdateReturn)
async def update_cart(
    data_obj: CartUpdate,
    current_user: AuthUser = Depends(get_current_verified_customer),
    cart_service: CartService = Depends(get_cart_service),
):

    return await cart_service.update_cart(
        data_obj=data_obj, customer_id=current_user.role_id
    )


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cart_item(
    product_id: int,
    current_user: AuthUser = Depends(get_current_verified_customer),
    cart_service: CartService = Depends(get_cart_service),
):
    return await cart_service.delete_cart_item(
        product_id=product_id, customer_id=current_user.role_id
    )


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
    current_user: AuthUser = Depends(get_current_verified_customer),
    cart_service: CartService = Depends(get_cart_service),
):

    await cart_service.clear_cart(customer_id=current_user.role_id)


@router.get("/summary", response_model=CartSummary)
async def get_cart_summary(
    current_user: AuthUser = Depends(get_current_verified_customer),
    cart_service: CartService = Depends(get_cart_service),
):

    return await cart_service.get_cart_summary(customer_id=current_user.role_id)


@router.post("/checkout")
async def checkout(
    data_obj: CheckoutCreate,
    current_user: AuthUser = Depends(get_current_verified_customer),
    cart_service: CartService = Depends(get_cart_service),
):

    return await cart_service.checkout(data_obj, current_user)


@router.get("/verify-payment/{payment_ref}", response_model=PaymentVerified)
async def verify_order_payment(
    payment_ref: str,
    current_user: AuthUser = Depends(get_current_verified_customer),
    cart_service: CartService = Depends(get_cart_service),
):
    return await cart_service.verify_order_payment(payment_ref=payment_ref)
