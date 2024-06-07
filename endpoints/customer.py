from fastapi import APIRouter, Depends, status, BackgroundTasks

from core.errors import InvalidRequest, ResourcesExist
from core.tokens import get_current_auth_user
from crud.auth import CRUDAuthUser, get_crud_auth_user
from crud.otp import crud_otp
from crud.customer import CRUDCustomer, get_crud_customer
from models.auth_user import AuthUser
from schemas import (
    CustomerCreate,
    CustomerReturn,
    OTPCreate,
    OTPType,
)
from schemas.base import RoleAuthDetailsUpdate, Roles

router = APIRouter(prefix="/customer", tags=["Customer"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=CustomerReturn)
async def create_customer(
    data_obj: CustomerCreate,
    background_tasks: BackgroundTasks,
    current_user: AuthUser = Depends(get_current_auth_user),
    crud_customer: CRUDCustomer = Depends(get_crud_customer),
    crud_auth_user: CRUDAuthUser = Depends(get_crud_auth_user),
):

    _, auth_user = crud_customer.get_by_auth_id(current_user.id)

    print(auth_user)

    if auth_user:
        raise ResourcesExist("customer exists")
    if current_user.default_role != Roles.CUSTOMER:
        raise InvalidRequest("Role must be customer to create customer account")
    if crud_customer.get_by_username(data_obj.username):
        raise ResourcesExist("username taken")
    data_obj.auth_id = current_user.id
    customer = await crud_customer.create(data_obj)
    customer_auth_details = RoleAuthDetailsUpdate(
        first_name=data_obj.first_name,
        last_name=data_obj.last_name,
        phone_number=data_obj.phone_number,
        role_id=customer.id,
    )
    print(customer_auth_details)
    background_tasks.add_task(
        crud_auth_user.update, current_user.id, customer_auth_details
    )
    otp_data_obj = OTPCreate(auth_id=current_user.id, otp_type=OTPType.PHONE_NUMBER)
    background_tasks.add_task(crud_otp.create, otp_data_obj)

    return customer
