from fastapi import APIRouter, Depends, status

from core.errors import InvalidRequest, MissingResources
from core.stripe_payment import create_checkout_session
from core.tokens import (
    get_current_verified_customer,
)
from crud import CRUDCart, CRUDProduct, get_crud_cart, get_crud_product, get_crud_order
from crud.customer import CRUDCustomer, get_crud_customer
from crud.product import CRUDOrder
from crud.vendor import CRUDVendor, get_crud_vendor
from models import AuthUser
from schemas import (
    CartCreate,
    CartReturn,
    CartUpdate,
    CartUpdateReturn,
    CartSummary,
    OrderCreate,
)
from schemas.base import PaymentType


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


@router.put("/{id}", response_model=CartUpdateReturn)
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


@router.get("/summary", response_model=CartSummary)
async def get_cart_summary(
    current_user: AuthUser = Depends(get_current_verified_customer),
    crud_cart: CRUDCart = Depends(get_crud_cart),
):
    cart_summary = await crud_cart.get_cart_summary(customer_id=current_user.role_id)
    return cart_summary


@router.post("/checkout")
async def place_order(
    data_obj: OrderCreate,
    current_user: AuthUser = Depends(get_current_verified_customer),
    crud_cart: CRUDCart = Depends(get_crud_cart),
    crud_order: CRUDOrder = Depends(get_crud_order),
    crud_customer: CRUDCustomer = Depends(get_crud_customer),
    crud_product: CRUDProduct = Depends(get_crud_product),
):
    customer = crud_customer.get_or_raise_exception(current_user.role_id)

    cart_summary = await crud_cart.get_cart_summary(customer_id=current_user.role_id)

    product_ids = [items.product_id for items in cart_summary["cart_items"]]
    products = [crud_product.get_or_raise_exception(id=id) for id in product_ids]

    if not data_obj.shipping_address:
        data_obj.shipping_address = (
            f"{customer.address} {customer.state} {customer.country}"
        )
    if not data_obj.contact_information:
        data_obj.contact_information = customer.phone_number

    data_obj.vendor_ids = [product.vendor_id for product in products]
    data_obj.customer_id = current_user.role_id
    data_obj.total_amount = cart_summary["total_amount"]

    new_order = await crud_order.create(data_obj)

    if data_obj.payment_type == PaymentType.CARD:
        await create_checkout_session(quantity=int(cart_summary["total_amount"]))

    return new_order
