from arq import ArqRedis
from fastapi import APIRouter, Depends, status

from core.errors import InvalidRequest
from core.paystack import PaystackClient, get_paystack
from core.stripe_payment import create_checkout_session
from core.tokens import (
    get_current_verified_customer,
)
from crud import (
    CRUDCart,
    CRUDProduct,
    CRUDOrder,
    CRUDPaymentDetails,
    CRUDOrderStatus,
    get_crud_cart,
    get_crud_product,
    get_crud_order,
    get_crud_payment_details,
    get_crud_order_status,
)
from models import AuthUser
from schemas import (
    CartCreate,
    CartReturn,
    CartUpdate,
    CartUpdateReturn,
    CartSummary,
    OrderCreate,
    OrderCreateBase,
    OrderStatusCreate,
    PaymentDetailsCreate,
)
from schemas.base import PaymentMethodEnum
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
    if crud_cart.get_by_product_id(product_id=data_obj.product_id):
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
    crud_product: CRUDProduct = Depends(get_crud_product),
):
    await crud_cart.check_if_product_id_exist_in_cart(
        customer_id=current_user.role_id, product_id=data_obj.product_id
    )

    products = crud_product.get_or_raise_exception(data_obj.product_id)

    if data_obj.quantity > products.stock:
        raise InvalidRequest(f"{products.stock} item stock Left")
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

    await crud_cart.delete_cart(current_user.role_id)


@router.get("/summary", response_model=CartSummary)
async def get_cart_summary(
    current_user: AuthUser = Depends(get_current_verified_customer),
    crud_cart: CRUDCart = Depends(get_crud_cart),
):
    cart_summary = await crud_cart.get_cart_summary(customer_id=current_user.role_id)
    return cart_summary


@router.post("/checkout")
async def checkout(
    data_obj: OrderCreate,
    current_user: AuthUser = Depends(get_current_verified_customer),
    crud_cart: CRUDCart = Depends(get_crud_cart),
    crud_order: CRUDOrder = Depends(get_crud_order),
    crud_order_status: CRUDOrderStatus = Depends(get_crud_order_status),
    crud_payment: CRUDPaymentDetails = Depends(get_crud_payment_details),
    queue_connection: ArqRedis = Depends(get_queue_connection),
):

    cart_summary = await crud_cart.get_cart_summary(customer_id=current_user.role_id)

    order_data_obj = OrderCreateBase(
        customer_id=current_user.role_id, total_amount=cart_summary["total_amount"]
    )
    products_and_quantity_in_cart_tuple = [
        (products.product, products.quantity) for products in cart_summary["cart_items"]
    ]

    products_quantities = []

    for product, quantity in products_and_quantity_in_cart_tuple:
        if quantity > product.stock:
            raise InvalidRequest(
                f"{product.product_name} has: {product.stock} stocks left"
            )
        products_quantities.append(product.stock - quantity)

    order = await crud_order.create(order_data_obj)
    await queue_connection.enqueue_job(
        "add_shipping_details", order, data_obj.shipping_details
    )
    await queue_connection.enqueue_job("add_order_items", order)

    if data_obj.payment_details.payment_method == PaymentMethodEnum.CARD:
        await create_checkout_session(quantity=int(cart_summary["total_amount"]))
    payment_details_obj = PaymentDetailsCreate(
        order_id=order.id,
        payment_method=data_obj.payment_details.payment_method,
        amount=order.total_amount,
    )
    await crud_payment.create(payment_details_obj)

    order_status_obj = OrderStatusCreate(order_id=order.id)
    await crud_order_status.create(order_status_obj)
    product_ids = [product.id for product, _ in products_and_quantity_in_cart_tuple]
    await queue_connection.enqueue_job(
        "update_stock_after_checkout", product_ids, products_quantities
    )

    return order


@router.get("/order")
async def get_all_orders(crud_order: CRUDOrder = Depends(get_crud_order)):
    return await crud_order.get_all_orders()


@router.get("/test-paystack")
async def get_all_orders(paystack: PaystackClient = Depends(get_paystack)):
    return await paystack.get_balance()
