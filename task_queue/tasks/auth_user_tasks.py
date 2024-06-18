from crud.auth import CRUDAuthUser
from crud.otp import CRUDOtp
from models.auth_user import AuthUser
from utils.password_utils import hash_password


async def update_auth_password(ctx, auth_id, password):
    crud_auth_user: CRUDAuthUser = ctx["crud_auth_user"]
    await crud_auth_user.update(
        id=auth_id,
        data_obj={AuthUser.PASSWORD: hash_password(password)},
    )


async def update_auth_details(ctx, auth_id, data_obj):
    crud_auth_user: CRUDAuthUser = ctx["crud_auth_user"]
    await crud_auth_user.update(
        id=auth_id,
        data_obj=data_obj,
    )


async def send_email_otp(ctx, data_obj):
    crud_otp: CRUDOtp = ctx["crud_otp"]

    crud_otp.create(data_obj)
