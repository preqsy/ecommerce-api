from fastapi import APIRouter, Depends, status

from api.dependencies.services import get_vendor_service
from core.tokens import get_current_auth_user
from models import AuthUser


from schemas import (
    VendorCreate,
    VendorReturn,
)

from services.vendor_service import VendorService


router = APIRouter(prefix="/vendor", tags=["Vendor"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=VendorReturn)
async def create_vendor(
    data_obj: VendorCreate,
    current_user: AuthUser = Depends(get_current_auth_user),
    vendor_service: VendorService = Depends(get_vendor_service),
):

    return await vendor_service.create_vendor(
        data_obj=data_obj, current_user=current_user
    )
