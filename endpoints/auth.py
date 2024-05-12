from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from core.db import get_db
from core.errors import ResourcesExist
from core.tokens import generate_tokens
from crud.auth import CRUDAuthUser, get_crud_auth_user
from schemas.auth import AuthUserCreate, AuthUserResponse
from models.auth_user import AuthUser
from utils.password_utils import hash_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthUserResponse)
async def register_user(
    data_obj: AuthUserCreate,
    db: Session = Depends(get_db),
    crud_auth_user: CRUDAuthUser = Depends(get_crud_auth_user),
):
    data_obj.email = data_obj.email.lower()
    email = crud_auth_user.get_by_email(data_obj.email)
    if email:
        raise ResourcesExist("Email Exists")
    data_obj.password = hash_password(data_obj.password)
    rsp_result = await crud_auth_user.create(data_obj)
    tokens = generate_tokens(user_id=rsp_result.id)
    return AuthUserResponse(auth_user=data_obj, tokens=tokens)
