from typing import List, Tuple
from arq import ArqRedis
from fastapi import APIRouter, Depends, status

from core.errors import InvalidRequest
from core.paystack import PaystackClient, get_paystack
from core.tokens import (
    get_current_verified_customer,
)
from crud import (
    CRUDCart,
    CRUDProduct,
    CRUDOrder,
    CRUDPaymentDetails,
    CRUDCustomer,
    get_crud_cart,
    get_crud_product,
    get_crud_order,
    get_crud_payment_details,
    get_crud_customer,
)
from models import AuthUser
from schemas import (
    CartCreate,
    CartReturn,
    CartUpdate,
    CartUpdateReturn,
    CartSummary,
    CheckoutCreate,
    OrderCreate,
    PaymentDetailsCreate,
)
from schemas.base import PaymentMethodEnum, StatusEnum
from schemas.order import PaymentVerified
from task_queue.main import get_queue_connection


router = APIRouter(prefix="/cart", tags=["Cart"])


@router.post("/add", status_code=status.HTTP_201_CREATED, response_model=CartReturn)
async def create_cart(
    data_obj: CartCreate,
    current_user: AuthUser = Depends(get_current_verified_customer),
    crud_cart: CRUDCart = Depends(get_crud_cart),
    crud_product: CRUDProduct = Depends(get_crud_product),
):
    product = crud_product.get_or_raise_exception(data_obj.product_id)
    cart_item = crud_cart.get_by_product_id(
        product_id=data_obj.product_id, customer_id=current_user.role_id
    )

    if cart_item and cart_item.customer_id == current_user.role_id:
        raise InvalidRequest("Already add item to cart")
    data_obj.customer_id = current_user.role_id
    if data_obj.quantity > product.stock:
        raise InvalidRequest(f"Stocks Available: {product.stock}")
    cart = await crud_cart.create(data_obj)

    return cart


@router.put("/", response_model=CartUpdateReturn)
async def update_cart(
    data_obj: CartUpdate,
    current_user: AuthUser = Depends(get_current_verified_customer),
    crud_cart: CRUDCart = Depends(get_crud_cart),
):
    product = await crud_cart.check_if_product_id_exist_in_cart(
        customer_id=current_user.role_id, product_id=data_obj.product_id
    )

    if product.id == data_obj.product_id:
        if data_obj.quantity > product.stock:
            raise InvalidRequest(f"{product.stock} item stock Left")

    updated_cart = await crud_cart.update_cart_by_customer_id(
        customer_id=current_user.role_id,
        data_obj=data_obj,
        product_id=data_obj.product_id,
    )

    return updated_cart


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cart_item(
    product_id: int,
    current_user: AuthUser = Depends(get_current_verified_customer),
    crud_cart: CRUDCart = Depends(get_crud_cart),
):
    await crud_cart.check_if_product_id_exist_in_cart(
        customer_id=current_user.role_id, product_id=product_id
    )

    await crud_cart.delete_cart_item_by_product_id(product_id=product_id)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
    current_user: AuthUser = Depends(get_current_verified_customer),
    crud_cart: CRUDCart = Depends(get_crud_cart),
):

    await crud_cart.clear_cart(current_user.role_id)


@router.get("/summary", response_model=CartSummary)
async def get_cart_summary(
    current_user: AuthUser = Depends(get_current_verified_customer),
    crud_cart: CRUDCart = Depends(get_crud_cart),
):
    cart_summary = await crud_cart.get_cart_summary(customer_id=current_user.role_id)
    return cart_summary


@router.post("/checkout")
async def checkout(
    data_obj: CheckoutCreate,
    current_user: AuthUser = Depends(get_current_verified_customer),
    crud_customer: CRUDCustomer = Depends(get_crud_customer),
    crud_cart: CRUDCart = Depends(get_crud_cart),
    crud_order: CRUDOrder = Depends(get_crud_order),
    crud_payment: CRUDPaymentDetails = Depends(get_crud_payment_details),
    queue_connection: ArqRedis = Depends(get_queue_connection),
    paystack: PaystackClient = Depends(get_paystack),
):

    cart_summary = await crud_cart.get_cart_summary(customer_id=current_user.role_id)
    customer = crud_customer.get_or_raise_exception(id=current_user.role_id)

    order_data_obj = OrderCreate(
        customer_id=current_user.role_id, total_amount=cart_summary["total_amount"]
    )
    products_and_quantity_in_cart: List[Tuple] = [
        (products.product, products.quantity) for products in cart_summary["cart_items"]
    ]

    for product, quantity in products_and_quantity_in_cart:
        if quantity > product.stock:
            raise InvalidRequest(
                f"{product.product_name} has: {product.stock} stocks left"
            )

    order = await crud_order.create(order_data_obj)
    await queue_connection.enqueue_job(
        "add_shipping_details", order, data_obj.shipping_details
    )
    await queue_connection.enqueue_job("add_order_items", order)
    paystack_metadata = {"order": order, "customer": customer}
    if (
        data_obj.payment_details.payment_method == PaymentMethodEnum.CARD
        or data_obj.payment_details.payment_method == PaymentMethodEnum.BANK_TRANSFER
    ):
        return await paystack.initialize_payment(
            amount=int(cart_summary["total_amount"]),
            email=current_user.email,
            channel=data_obj.payment_details.payment_method,
            **paystack_metadata,
        )

    payment_details_obj = PaymentDetailsCreate(
        order_id=order.id,
        payment_method=data_obj.payment_details.payment_method,
        amount=order.total_amount,
    )
    await crud_payment.create(payment_details_obj)

    await queue_connection.enqueue_job("update_stock_after_checkout", order.id)

    return order


@router.get("/verify-payment/{payment_ref}", response_model=PaymentVerified)
async def verify_order_payment(
    payment_ref: str,
    current_user: AuthUser = Depends(get_current_verified_customer),
    crud_payment: CRUDPaymentDetails = Depends(get_crud_payment_details),
    crud_order: CRUDOrder = Depends(get_crud_order),
    queue_connection: ArqRedis = Depends(get_queue_connection),
    paystack: PaystackClient = Depends(get_paystack),
):
    payment_details = crud_payment.get_by_payment_ref(payment_ref=payment_ref)

    if payment_details:
        raise InvalidRequest("Payment Already Successful")

    payment_rsp = await paystack.verify_payment(payment_ref=payment_ref)
    order_id = payment_rsp["metadata"]["order_id"]

    match payment_rsp["status"]:
        case StatusEnum.ABADONED:
            raise InvalidRequest(
                "You have a pending transaction, Complete Your Payment"
            )
        case StatusEnum.FAILED:
            await crud_order.delete(id=order_id)
            raise InvalidRequest("Payment Failed, Checkout again and complete Payment ")
        case StatusEnum.SUCCESS:
            pass
        case _:
            await crud_order.delete(id=order_id)
            raise InvalidRequest("Contact Paystack and try again")

    payment_details_obj = PaymentDetailsCreate(
        order_id=order_id,
        payment_method=payment_rsp["channel"],
        amount=payment_rsp["amount"] / 100,
        payment_ref=payment_rsp["reference"],
        status=StatusEnum.SUCCESS,
        paid_at=payment_rsp["paid_at"],
    )
    await queue_connection.enqueue_job("update_stock_after_checkout", order_id)
    await crud_payment.create(payment_details_obj)

    return PaymentVerified
