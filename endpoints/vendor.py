from arq import ArqRedis
from fastapi import APIRouter, Depends, Query, status, BackgroundTasks

from core.errors import InvalidRequest, ResourcesExist
from core.tokens import get_current_auth_user
from crud import (
    CRUDVendor,
    CRUDOrderItem,
    CRUDOtp,
    get_crud_vendor,
    get_crud_otp,
    get_crud_order_item,
)
from models import AuthUser


from schemas import (
    OTPCreate,
    OTPType,
    VendorCreate,
    VendorReturn,
    VendorDashboardReturn,
    TotalSalesReturn,
)

from schemas.base import RoleAuthDetailsUpdate, Roles
from task_queue.main import get_queue_connection


router = APIRouter(prefix="/vendor", tags=["Vendor"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=VendorReturn)
async def create_vendor(
    data_obj: VendorCreate,
    background_tasks: BackgroundTasks,
    current_user: AuthUser = Depends(get_current_auth_user),
    crud_vendor: CRUDVendor = Depends(get_crud_vendor),
    queue_connection: ArqRedis = Depends(get_queue_connection),
    crud_otp: CRUDOtp = Depends(get_crud_otp),
):

    auth_user = crud_vendor.get_by_auth_id(current_user.id)

    if auth_user:
        raise ResourcesExist("Vendor exists")
    if current_user.default_role != Roles.VENDOR:
        raise InvalidRequest("Role must be Vendor to create vendor account")
    if crud_vendor.get_by_username(data_obj.username):
        raise ResourcesExist("username taken")
    data_obj.auth_id = current_user.id
    vendor = await crud_vendor.create(data_obj)
    vendor_auth_details = RoleAuthDetailsUpdate(
        first_name=data_obj.first_name,
        last_name=data_obj.last_name,
        phone_number=data_obj.phone_number,
        role_id=vendor.id,
    )
    await queue_connection.enqueue_job(
        "update_auth_details", current_user.id, vendor_auth_details
    )
    otp_data_obj = OTPCreate(auth_id=current_user.id, otp_type=OTPType.PHONE_NUMBER)
    background_tasks.add_task(crud_otp.create, otp_data_obj)
    return vendor


@router.get("/dashboard/activity", response_model=VendorDashboardReturn)
async def vendor_dashboard(
    current_user: AuthUser = Depends(get_current_auth_user),
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


@router.get("/dashboard/sales/date", response_model=TotalSalesReturn)
async def get_sales_activity_by_date(
    days: int = Query(default=7),
    current_user: AuthUser = Depends(get_current_auth_user),
    crud_order_item: CRUDOrderItem = Depends(get_crud_order_item),
):
    order_items = await crud_order_item.get_order_items_by_vendor_id_and_date(
        vendor_id=current_user.role_id, days=days
    )
    if not order_items:
        raise InvalidRequest("No Orders Completed Yet")
    total_sales = sum([item.price * item.quantity for item in order_items])
    total_sales = {"total_sales": total_sales}
    return total_sales
