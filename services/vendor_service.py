from arq import ArqRedis
from fastapi import BackgroundTasks

from core.errors import InvalidRequest, ResourcesExist
from crud import CRUDAuthUser, CRUDOtp, CRUDVendor
from models.auth_user import AuthUser
from schemas.base import RoleAuthDetailsUpdate, Roles
from schemas import OTPCreate, OTPType, VendorCreate


class VendorService:

    def __init__(
        self,
        crud_auth_user: CRUDAuthUser,
        crud_otp: CRUDOtp,
        crud_vendor: CRUDVendor,
        queue_connection: ArqRedis,
    ):
        self.crud_auth_user = crud_auth_user
        self.crud_vendor = crud_vendor
        self.crud_otp = crud_otp
        self.queue_connection = queue_connection

    async def create_vendor(
        self,
        data_obj: VendorCreate,
        background_tasks: BackgroundTasks,
        current_user: AuthUser,
    ):

        auth_user = self.crud_vendor.get_by_auth_id(current_user.id)

        if auth_user:
            raise ResourcesExist("Vendor exists")
        if current_user.default_role != Roles.VENDOR:
            raise InvalidRequest("Role must be Vendor to create vendor account")
        if self.crud_vendor.get_by_username(data_obj.username):
            raise ResourcesExist("username taken")
        data_obj.auth_id = current_user.id
        vendor = await self.crud_vendor.create(data_obj)
        vendor_auth_details = RoleAuthDetailsUpdate(
            first_name=data_obj.first_name,
            last_name=data_obj.last_name,
            phone_number=data_obj.phone_number,
            role_id=vendor.id,
        )
        await self.queue_connection.enqueue_job(
            "update_auth_details", current_user.id, vendor_auth_details
        )
        otp_data_obj = OTPCreate(auth_id=current_user.id, otp_type=OTPType.PHONE_NUMBER)
        background_tasks.add_task(self.crud_otp.create, otp_data_obj)
        return vendor
