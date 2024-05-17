from fastapi import Depends, APIRouter, status, UploadFile

from core.tokens import get_current_verified_vendor
from crud.product import CRUDProduct, get_crud_product
from models.auth_user import AuthUser
from schemas.product import ProductCreate

router = APIRouter(prefix="/product", tags=["Product"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_product(
    data_obj: ProductCreate,
    current_user: AuthUser = Depends(get_current_verified_vendor),
    crud_product: CRUDProduct = Depends(get_crud_product),
    file=UploadFile(...),
):

    product = await crud_product.create(data_obj)
    return "Hello World"
