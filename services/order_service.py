from core.errors import InvalidRequest
from crud import (
    CRUDCustomer,
    CRUDOrder,
    CRUDOrderItem,
)
from schemas.base import OrderStatusEnum
from schemas import OrderItemStatus


class OrderService:

    def __init__(
        self,
        crud_customer: CRUDCustomer,
        crud_order: CRUDOrder,
        crud_order_item: CRUDOrderItem,
    ):

        self.crud_customer = crud_customer
        self.crud_order = crud_order
        self.crud_order_item = crud_order_item

    async def get_all_orders(self):
        return await self.crud_order.get_all_orders()

    async def vendor_dashboard(self, vendor_id: int):

        order_items = await self.crud_order_item.get_order_items_by_vendor_id(
            vendor_id=vendor_id
        )
        if not order_items:
            raise InvalidRequest("No Orders Completed Yet")

        total_sales = sum([item.price * item.quantity for item in order_items])
        dashboard = {"total_sales": total_sales, "total_orders": len(order_items)}

        return dashboard

    async def get_sales_activity_by_date(self, days: int, vendor_id: int):
        order_items = await self.crud_order_item.get_order_items_by_vendor_id_and_date(
            vendor_id=vendor_id, days=days
        )
        if not order_items:
            raise InvalidRequest("No Orders Completed Yet")
        total_sales = sum([item.price * item.quantity for item in order_items])
        total_sales_and_quantity = {
            "total_sales": total_sales,
            "total_orders": len(order_items),
        }
        return total_sales_and_quantity

    async def get_vendors_orders(self, vendor_id: int):
        order_items = await self.crud_order_item.get_order_items_by_vendor_id(
            vendor_id=vendor_id
        )
        return order_items

    async def update_order_status(
        self,
        order_item_id: int,
        vendor_id: int,
        data_obj: OrderItemStatus,
    ):
        order_item = self.crud_order_item.get_or_raise_exception(id=order_item_id)
        if order_item.vendor_id != vendor_id:
            raise InvalidRequest("Not Your Item")
        if order_item.status == OrderStatusEnum.PROCESSING:
            return await self.crud_order_item.update(
                id=order_item_id, data_obj={data_obj.STATUS: data_obj.status}
            )
        raise InvalidRequest("Item Status has been changed to Shipped or Refunded")
