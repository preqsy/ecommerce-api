from datetime import datetime, timedelta, timezone
from fastapi import Depends
from sqlalchemy import desc

from core.db import get_db
from core.errors import InvalidRequest
from crud.base import CRUDBase
from models.auth_user import OTP
from schemas import OTPCreate
from utils.generate_otp import generate_otp
from utils.send_email import send_email


class CRUDOtp(CRUDBase[OTP, OTPCreate, OTPCreate]):

    async def send_and_create_otp(
        self, data_obj: OTPCreate, email, no_of_tries: int = 0
    ) -> bool:
        if not data_obj.token:
            data_obj.token = generate_otp()
        await send_email(receiver_email=email, otp=data_obj.token)
        new_otp = OTP(
            auth_id=data_obj.auth_id,
            otp=data_obj.token,
            otp_type=data_obj.otp_type,
            no_of_tries=no_of_tries + 1,
        )
        self._db.add(new_otp)
        self._db.commit()
        self._db.refresh(new_otp)
        return True

    async def verify_otp(self, token, auth_id, otp_type) -> bool:
        otp_query = self.get_by_auth_id(auth_id)
        if otp_query is None or otp_query.otp != token:
            return False
        if otp_query.otp_type != otp_type:
            raise InvalidRequest("Invalid Otp Type")

        current_time = datetime.now(timezone.utc)
        created_timestamp = otp_query.created_timestamp
        expiration_time = created_timestamp + timedelta(minutes=10)

        if current_time > expiration_time:
            await self.delete(otp_query.id)
            raise InvalidRequest("OTP has expired")
        await self.delete(id=otp_query.id)
        return True

    async def check_number_of_trials(self, auth_id):
        otp_query = (
            self._db.query(self.model)
            .filter(self.model.auth_id == auth_id)
            .order_by(desc(self.model.id))
            .first()
        )
        return otp_query


crud_otp = CRUDOtp(db=get_db(), model=OTP)


def get_crud_otp(db=Depends(get_db)):
    return CRUDOtp(db=db, model=OTP)
