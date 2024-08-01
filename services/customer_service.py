from arq import ArqRedis

from core.errors import InvalidRequest, ResourcesExist
from crud import CRUDAuthUser, CRUDOtp, CRUDCustomer
from models import AuthUser
from schemas.base import RoleAuthDetailsUpdate, Roles
from schemas import CustomerCreate, OTPCreate, OTPType


class CustomerService:

    def __init__(
        self,
        crud_auth_user: CRUDAuthUser,
        crud_otp: CRUDOtp,
        crud_customer: CRUDCustomer,
        queue_connection: ArqRedis,
    ):
        self.crud_auth_user = crud_auth_user
        self.crud_customer = crud_customer
        self.crud_otp = crud_otp
        self.queue_connection = queue_connection

    async def create_customer(
        self,
        data_obj: CustomerCreate,
        current_user: AuthUser,
    ):

        auth_user = self.crud_customer.get_by_auth_id(current_user.id)

        if auth_user:
            raise ResourcesExist("customer exists")
        if current_user.default_role != Roles.CUSTOMER:
            raise InvalidRequest("Role must be customer to create customer account")
        if self.crud_customer.get_by_username(data_obj.username):
            raise ResourcesExist("username taken")
        data_obj.auth_id = current_user.id
        customer = await self.crud_customer.create(data_obj)
        customer_auth_details = RoleAuthDetailsUpdate(
            first_name=data_obj.first_name,
            last_name=data_obj.last_name,
            phone_number=data_obj.phone_number,
            role_id=customer.id,
        )

        await self.queue_connection.enqueue_job(
            "update_auth_details", current_user.id, customer_auth_details
        )
        otp_data_obj = OTPCreate(auth_id=current_user.id, otp_type=OTPType.PHONE_NUMBER)
        await self.queue_connection.enqueue_job(
            "send_email_otp", otp_data_obj, current_user.email
        )

        return customer
