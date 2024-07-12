from fastapi import APIRouter, Depends, Query

from core.errors import InvalidRequest
from core.tokens import get_current_verified_vendor
from crud import (
    CRUDOrderItem,
    CRUDOrder,
    get_crud_order_item,
    get_crud_order,
)
from models import AuthUser


from schemas import TotalSalesReturn, OrdersWithCustomerDetails, OrderItemStatus

from schemas.base import OrderStatusEnum


router = APIRouter(prefix="/order", tags=["Order"])


@router.get("/")
async def get_all_orders(crud_order: CRUDOrder = Depends(get_crud_order)):
    return await crud_order.get_all_orders()


@router.get("/vendor/activity", response_model=TotalSalesReturn)
async def vendor_dashboard(
    current_user: AuthUser = Depends(get_current_verified_vendor),
    crud_order_item: CRUDOrderItem = Depends(get_crud_order_item),
):

    order_items = await crud_order_item.get_order_items_by_vendor_id(
        vendor_id=current_user.role_id
    )
    if not order_items:
        raise InvalidRequest("No Orders Completed Yet")

    total_sales = sum([item.price * item.quantity for item in order_items])
    dashboard = {"total_sales": total_sales, "total_orders": len(order_items)}

    return dashboard


@router.get("/vendor/sales/date", response_model=TotalSalesReturn)
async def get_sales_activity_by_date(
    days: int = Query(default=7),
    current_user: AuthUser = Depends(get_current_verified_vendor),
    crud_order_item: CRUDOrderItem = Depends(get_crud_order_item),
):
    order_items = await crud_order_item.get_order_items_by_vendor_id_and_date(
        vendor_id=current_user.role_id, days=days
    )
    if not order_items:
        raise InvalidRequest("No Orders Completed Yet")
    total_sales = sum([item.price * item.quantity for item in order_items])
    total_sales_and_quantity = {
        "total_sales": total_sales,
        "total_orders": len(order_items),
    }
    return total_sales_and_quantity


@router.get("/vendor/", response_model=list[OrdersWithCustomerDetails])
async def get_vendors_orders(
    current_user: AuthUser = Depends(get_current_verified_vendor),
    crud_order_item: CRUDOrderItem = Depends(get_crud_order_item),
):
    order_items = await crud_order_item.get_order_items_by_vendor_id(
        vendor_id=current_user.role_id
    )
    return order_items


@router.put(
    "/order-items/{order_item_id}/status",
)
async def update_order_status(
    order_item_id: int,
    data_obj: OrderItemStatus,
    current_user: AuthUser = Depends(get_current_verified_vendor),
    crud_order_item: CRUDOrderItem = Depends(get_crud_order_item),
):
    order_item = crud_order_item.get_or_raise_exception(id=order_item_id)
    if order_item.vendor_id != current_user.role_id:
        raise InvalidRequest("Cannot Perform Specified")
    if order_item.status == OrderStatusEnum.PROCESSING:
        return await crud_order_item.update(
            id=order_item_id, data_obj={data_obj.STATUS: data_obj.status}
        )
    raise InvalidRequest("Item Status has been changed to Shipped or Refunded")
