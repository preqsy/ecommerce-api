from fastapi import APIRouter, Depends, status

from core.errors import InvalidRequest, MissingResources
from core.tokens import (
    get_current_verified_customer,
)
from crud.product import CRUDCart, CRUDProduct, get_crud_cart, get_crud_product
from models import AuthUser
from schemas import CartCreate, CartReturn, CartUpdate


router = APIRouter(prefix="/cart", tags=["Cart"])


@router.post("/add", status_code=status.HTTP_201_CREATED, response_model=CartReturn)
async def create_cart(
    data_obj: CartCreate,
    current_user: AuthUser = Depends(get_current_verified_customer),
    crud_cart: CRUDCart = Depends(get_crud_cart),
    crud_product: CRUDProduct = Depends(get_crud_product),
):
    product = crud_product.get_or_raise_exception(data_obj.product_id)
    data_obj.customer_id = current_user.role_id
    cart = await crud_cart.create(data_obj)

    return cart


@router.get("/carts")
def get_carts(
    current_user: AuthUser = Depends(get_current_verified_customer),
    crud_cart: CRUDCart = Depends(get_crud_cart),
):
    cart_items = crud_cart.get_cart_items(current_user.role_id)
    total_amount = 0.0
    if not cart_items:
        raise MissingResources("No items in cart")
    for item in cart_items:
        amount = item.quantity * item.product.price
        total_amount = total_amount + amount
    # TODO: Add a response model
    cart_details = {"cart_items": cart_items, "total_amount": total_amount}
    return cart_details


@router.put("/{id}")
async def update_cart(
    id: int,
    data_obj: CartUpdate,
    current_user: AuthUser = Depends(get_current_verified_customer),
    crud_cart: CRUDCart = Depends(get_crud_cart),
):
    cart_item = crud_cart.get_or_raise_exception(id)
    if cart_item.customer_id != current_user.role_id:
        InvalidRequest("Can't update cart")
    updated_cart = await crud_cart.update(id=id, data_obj=data_obj)

    return updated_cart


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cart_item(
    id: int,
    current_user: AuthUser = Depends(get_current_verified_customer),
    crud_cart: CRUDCart = Depends(get_crud_cart),
):
    cart_item = crud_cart.get_or_raise_exception(id)
    if cart_item.customer_id != current_user.role_id:
        InvalidRequest("Can't update cart")
    await crud_cart.delete(id)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
    current_user: AuthUser = Depends(get_current_verified_customer),
    crud_cart: CRUDCart = Depends(get_crud_cart),
):

    await crud_cart.delete_cart(current_user.role_id)


@router.get("/summary")
def get_cart_summary(
    current_user: AuthUser = Depends(get_current_verified_customer),
    crud_cart: CRUDCart = Depends(get_crud_cart),
):
    cart_items = crud_cart.get_cart_items(current_user.role_id)
    if not cart_items:
        raise MissingResources("No items in cart")

    total_amount = sum(item.quantity * item.product.price for item in cart_items)
    total_items = sum(item.quantity for item in cart_items)

    summary = {
        "total_items": total_items,
        "total_amount": total_amount,
        "items": cart_items,
    }

    return summary
