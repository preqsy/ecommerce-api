from crud import CRUDOrder

from models import Order
from schemas.base import OrderStatusEnum


async def check_order_items_and_update_order_status_to_shipped(ctx):
    crud_order: CRUDOrder = ctx["crud_order"]

    orders = await crud_order.get_all_orders()
    order_items = [
        order.order_items
        for order in orders
        if order.status == OrderStatusEnum.PROCESSING
    ]

    order_items_iter = iter(order_items)
    for index in range(len(order_items)):
        order_items = next(order_items_iter)
        order_id = order_items[index].order_id
        status = [item.status for item in order_items]

        if OrderStatusEnum.PROCESSING in status or OrderStatusEnum.REFUNDED in status:
            pass
        else:
            await crud_order.update(
                id=order_id, data_obj={Order.STATUS: OrderStatusEnum.SHIPPED}
            )
