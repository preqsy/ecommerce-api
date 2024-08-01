from fastapi import APIRouter, Depends, status

from api.dependencies.services import get_customer_service
from core.tokens import get_current_auth_user

from models.auth_user import AuthUser
from schemas import (
    CustomerCreate,
    CustomerReturn,
)
from services.customer_service import CustomerService

router = APIRouter(prefix="/customer", tags=["Customer"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=CustomerReturn)
async def create_customer(
    data_obj: CustomerCreate,
    current_user: AuthUser = Depends(get_current_auth_user),
    customer_service: CustomerService = Depends(get_customer_service),
):

    return await customer_service.create_customer(
        data_obj=data_obj, current_user=current_user
    )
