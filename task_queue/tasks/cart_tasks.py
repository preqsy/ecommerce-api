from typing import List, Tuple

from crud import CRUDProduct
from crud import CRUDCustomer, CRUDShippingDetails, CRUDOrderItem, CRUDCart
from models import Product
from models.order import Order
from schemas import ShippingDetailsCreate, OrderItemsCreate


async def add_shipping_details(
    ctx, order: Order, shipping_details: ShippingDetailsCreate
):
    crud_customer: CRUDCustomer = ctx["crud_customer"]
    crud_shipping_details: CRUDShippingDetails = ctx["crud_shipping_details"]

    customer = crud_customer.get_or_raise_exception(id=order.customer_id)

    shipping_details.contact_information = (
        shipping_details.contact_information
        if shipping_details.contact_information
        else customer.phone_number
    )
    shipping_details.address = (
        shipping_details.address if shipping_details.address else customer.address
    )
    shipping_details.state = (
        shipping_details.state if shipping_details.state else customer.state
    )
    shipping_details.country = (
        shipping_details.country if shipping_details.country else customer.country
    )
    shipping_details.order_id = order.id
    await crud_shipping_details.create(shipping_details)


async def add_order_items(ctx, order: Order):

    crud_order_item: CRUDOrderItem = ctx["crud_order_item"]
    crud_cart: CRUDCart = ctx["crud_cart"]

    cart_summary = await crud_cart.get_cart_summary(customer_id=order.customer_id)

    products_and_quantity_in_cart_tuple = [
        (products.product, products.quantity) for products in cart_summary["cart_items"]
    ]
    for product, quantity in products_and_quantity_in_cart_tuple:
        order_item = OrderItemsCreate(
            order_id=order.id,  # type: ignore
            vendor_id=product.vendor_id,
            price=product.price,
            quantity=quantity,
            product_id=product.id,
        )
        await crud_order_item.create(order_item)
    return


async def update_stock_after_checkout(ctx, order_id):
    crud_order_item: CRUDOrderItem = ctx["crud_order_item"]
    crud_product: CRUDProduct = ctx["crud_product"]

    order_items = crud_order_item.get_by_order_id(order_id)
    product_id_and_quantity: List[Tuple[int]] = [
        (item.product_id, item.quantity) for item in order_items
    ]
    for product_id, cart_item_quantity in product_id_and_quantity:
        product = crud_product.get_or_raise_exception(id=product_id)
        quantity = product.stock - cart_item_quantity
        await crud_product.update(id=product_id, data_obj={Product.STOCK: quantity})
    return
