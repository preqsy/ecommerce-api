from typing import List

from crud import CRUDProduct
from crud import CRUDCustomer, CRUDShippingDetails, CRUDOrderItem, CRUDCart
from models import Product
from models.orders import Order
from schemas import ShippingDetailsCreate, OrderItemsCreate


async def update_stock_after_checkout(ctx, product_ids: List, new_stock: int):
    crud_product: CRUDProduct = ctx["crud_product"]

    for index, ids in enumerate(product_ids):
        crud_product.get_or_raise_exception(ids)
        await crud_product.update(id=ids, data_obj={Product.STOCK: new_stock[index]})


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
            order_id=order.id,
            vendor_id=product.vendor_id,
            price=product.price,
            quantity=quantity,
            product_id=product.id,
        )
        await crud_order_item.create(order_item)
