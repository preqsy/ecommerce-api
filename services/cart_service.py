from typing import List, Tuple
from arq import ArqRedis

from core.errors import InvalidRequest
from core.paystack import PaystackClient
from crud import (
    CRUDAuthUser,
    CRUDProduct,
    CRUDCart,
    CRUDCustomer,
    CRUDOrder,
    CRUDPaymentDetails,
)
from models import AuthUser
from schemas.base import PaymentMethodEnum, StatusEnum
from schemas import (
    CartCreate,
    CartUpdate,
    CheckoutCreate,
    OrderCreate,
    PaymentDetailsCreate,
    PaymentVerified,
)


class CartService:

    def __init__(
        self,
        crud_auth_user: CRUDAuthUser,
        crud_product: CRUDProduct,
        crud_cart: CRUDCart,
        queue_connection: ArqRedis,
        crud_customer: CRUDCustomer,
        crud_order: CRUDOrder,
        crud_payment: CRUDPaymentDetails,
        paystack: PaystackClient,
    ):
        self.crud_auth_user = crud_auth_user
        self.crud_product = crud_product
        self.crud_cart = crud_cart
        self.crud_customer = crud_customer
        self.crud_order = crud_order
        self.crud_payment = crud_payment
        self.paystack = paystack
        self.queue_connection = queue_connection

    async def create_cart(self, data_obj: CartCreate, customer_id: int):
        product = self.crud_product.get_or_raise_exception(data_obj.product_id)
        cart_item = self.crud_cart.get_by_product_id_and_customer_id(
            product_id=data_obj.product_id, customer_id=customer_id
        )

        if cart_item and cart_item.customer_id == customer_id:
            raise InvalidRequest("Already add item to cart")
        data_obj.customer_id = customer_id
        if data_obj.quantity > product.stock:
            raise InvalidRequest(f"Stocks Available: {product.stock}")
        cart = await self.crud_cart.create(data_obj)

        return cart

    async def update_cart(self, data_obj: CartUpdate, customer_id: int):
        product = await self.crud_cart.check_if_product_id_exist_in_cart(
            customer_id=customer_id, product_id=data_obj.product_id
        )

        if product.id == data_obj.product_id:
            if data_obj.quantity > product.stock:
                raise InvalidRequest(f"{product.stock} item stock Left")

        updated_cart = await self.crud_cart.update_cart_by_customer_id(
            customer_id=customer_id,
            data_obj=data_obj,
            product_id=data_obj.product_id,
        )

        return updated_cart

    async def delete_cart_item(self, product_id: int, customer_id: int):
        await self.crud_cart.check_if_product_id_exist_in_cart(
            customer_id=customer_id, product_id=product_id
        )

        await self.crud_cart.delete_cart_item_by_product_id(product_id=product_id)

    async def clear_cart(self, customer_id: int):
        await self.crud_cart.clear_cart(customer_id)

    async def get_cart_summary(self, customer_id: int):
        cart_summary = await self.crud_cart.get_cart_summary(customer_id=customer_id)
        return cart_summary

    async def checkout(
        self,
        data_obj: CheckoutCreate,
        current_user: AuthUser,
    ):

        cart_summary = await self.crud_cart.get_cart_summary(
            customer_id=current_user.role_id
        )
        customer = self.crud_customer.get(id=current_user.role_id)

        order_data_obj = OrderCreate(
            customer_id=current_user.role_id, total_amount=cart_summary["total_amount"]
        )
        products_and_quantity_in_cart: List[Tuple] = [
            (products.product, products.quantity)
            for products in cart_summary["cart_items"]
        ]

        for product, quantity in products_and_quantity_in_cart:
            if quantity > product.stock:
                raise InvalidRequest(
                    f"{product.product_name} has: {product.stock} stocks left"
                )

        order = await self.crud_order.create(order_data_obj)
        await self.queue_connection.enqueue_job(
            "add_shipping_details", order, data_obj.shipping_details
        )
        await self.queue_connection.enqueue_job("add_order_items", order)
        paystack_metadata = {"order": order, "customer": customer}
        if (
            data_obj.payment_details.payment_method == PaymentMethodEnum.CARD
            or data_obj.payment_details.payment_method
            == PaymentMethodEnum.BANK_TRANSFER
        ):
            return await self.paystack.initialize_payment(
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
        await self.crud_payment.create(payment_details_obj)

        await self.queue_connection.enqueue_job("update_stock_after_checkout", order.id)

        return order

    async def verify_order_payment(
        self,
        payment_ref: str,
    ):
        payment_details = self.crud_payment.get_by_payment_ref(payment_ref=payment_ref)

        if payment_details:
            raise InvalidRequest("Payment Already Successful")

        payment_rsp = await self.paystack.verify_payment(payment_ref=payment_ref)
        order_id = payment_rsp["metadata"]["order_id"]

        match payment_rsp["status"]:
            case StatusEnum.ABADONED:
                raise InvalidRequest(
                    "You have a pending transaction, Complete Your Payment"
                )
            case StatusEnum.FAILED:
                await self.crud_order.delete(id=order_id)
                raise InvalidRequest(
                    "Payment Failed, Checkout again and complete Payment "
                )
            case StatusEnum.SUCCESS:
                pass
            case _:
                await self.crud_order.delete(id=order_id)
                raise InvalidRequest("Contact Paystack and try again")

        payment_details_obj = PaymentDetailsCreate(
            order_id=order_id,
            payment_method=payment_rsp["channel"],
            amount=payment_rsp["amount"] / 100,
            payment_ref=payment_rsp["reference"],
            status=StatusEnum.SUCCESS,
            paid_at=payment_rsp["paid_at"],
        )
        await self.queue_connection.enqueue_job("update_stock_after_checkout", order_id)
        await self.crud_payment.create(payment_details_obj)

        return PaymentVerified
