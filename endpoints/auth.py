from fastapi import APIRouter, Depends, BackgroundTasks, status
from sqlalchemy.orm import Session

from core.db import get_db
from core.errors import InvalidRequest, MissingResources, ResourcesExist
from core.tokens import generate_tokens
from crud.auth import CRUDAuthUser, get_crud_auth_user
from crud.otp import CRUDOtp, crud_otp, get_crud_otp
from schemas.auth import (
    AuthUserCreate,
    AuthUserResponse,
    RegisterAuthUserResponse,
    VerifiedEmail,
)
from models.auth_user import AuthUser, RefreshToken
from schemas.otp import OTPCreate
from utils.email_validation import email_validate
from utils.password_utils import hash_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=RegisterAuthUserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    data_obj: AuthUserCreate,
    background_task: BackgroundTasks,
    db: Session = Depends(get_db),
    crud_auth_user: CRUDAuthUser = Depends(get_crud_auth_user),
):
    data_obj.email = data_obj.email.lower()
    if not email_validate(data_obj.email):
        raise InvalidRequest("Invalid Email")
    email = crud_auth_user.get_by_email(data_obj.email)
    if email:
        raise ResourcesExist("Email Exists")
    data_obj.password = hash_password(data_obj.password)
    new_user = await crud_auth_user.create(data_obj)
    background_task.add_task(crud_otp.create, new_user.id)
    tokens = generate_tokens(user_id=new_user.id)
    refresh_token = RefreshToken(
        refresh_token=tokens.refresh_token, auth_id=new_user.id
    )
    db.add(refresh_token)
    db.commit()
    new_user_dict = data_obj.model_dump()
    new_user_dict[AuthUserResponse.ID] = new_user.id
    return RegisterAuthUserResponse(auth_user=new_user_dict, tokens=tokens)


@router.post("/verify", response_model=VerifiedEmail)
async def verify_email(
    data_obj: OTPCreate,
    crud_otp: CRUDOtp = Depends(get_crud_otp),
    crud_auth_user: CRUDAuthUser = Depends(get_crud_auth_user),
):
    if not crud_auth_user.get_or_raise_execption(id=data_obj.auth_id):
        MissingResources
    otp_verify = await crud_otp.verify_otp(
        token=data_obj.token, auth_id=data_obj.auth_id
    )
    if not otp_verify:
        raise InvalidRequest("Invalid OTP")
    await crud_auth_user.update(
        id=data_obj.auth_id, data_dict={AuthUser.EMAIL_VERIFIED: True}
    )
    return VerifiedEmail(email_verified=True)
