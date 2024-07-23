from fastapi import APIRouter, Depends, Query

from api.dependencies.services import get_order_service
from core.tokens import get_current_verified_vendor
from models import AuthUser


from schemas import TotalSalesReturn, OrderItemStatus, VendorOrderReturn

from services.order_service import OrderService


router = APIRouter(prefix="/order", tags=["Order"])


@router.get("/")
async def get_all_orders(
    order_service: OrderService = Depends(get_order_service),
):
    return await order_service.get_all_orders()


@router.get("/vendor/activity", response_model=TotalSalesReturn)
async def vendor_dashboard(
    current_user: AuthUser = Depends(get_current_verified_vendor),
    order_service: OrderService = Depends(get_order_service),
):

    return await order_service.vendor_dashboard(vendor_id=current_user.role_id)


@router.get("/vendor/sales/date", response_model=TotalSalesReturn)
async def get_sales_activity_by_date(
    days: int = Query(default=7),
    current_user: AuthUser = Depends(get_current_verified_vendor),
    order_service: OrderService = Depends(get_order_service),
):
    return await order_service.get_sales_activity_by_date(
        days=days, vendor_id=current_user.role_id
    )


@router.get("/vendor/", response_model=list[VendorOrderReturn])
async def get_vendors_orders_items(
    current_user: AuthUser = Depends(get_current_verified_vendor),
    order_service: OrderService = Depends(get_order_service),
):

    return await order_service.get_vendors_order_items(vendor_id=current_user.role_id)


@router.put(
    "/order-items/{order_item_id}/status",
)
async def update_order_status(
    order_item_id: int,
    data_obj: OrderItemStatus,
    current_user: AuthUser = Depends(get_current_verified_vendor),
    order_service: OrderService = Depends(get_order_service),
):
    return await order_service.update_order_status(
        data_obj=data_obj, order_item_id=order_item_id, vendor_id=current_user.role_id
    )
