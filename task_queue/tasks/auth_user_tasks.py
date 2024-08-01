import logging

from crud import CRUDAuthUser, CRUDOtp
from models import AuthUser
from utils.password_utils import hash_password


logger = logging.getLogger(__name__)


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


async def send_email_otp(ctx, data_obj, email):
    crud_otp: CRUDOtp = ctx["crud_otp"]

    try:
        await crud_otp.send_and_create_otp(data_obj, email)
        logger.info(f"OTP Successfull Sent to {email}")
    except Exception as e:
        logger.error(e)
