from fastapi import Depends
from sqlalchemy import desc

from core.db import get_db
from core.errors import InvalidRequest
from crud.base import CRUDBase
from models.auth_user import OTP
from schemas import OTPCreate
from utils.generate_otp import generate_otp


class CRUDOtp(CRUDBase[OTP, OTPCreate, OTPCreate]):

    def create(self, data_obj: OTPCreate) -> bool:
        data_obj.token = generate_otp()
        new_otp = OTP(
            auth_id=data_obj.auth_id, otp=data_obj.token, otp_type=data_obj.otp_type
        )
        self._db.add(new_otp)
        self._db.commit()
        self._db.refresh(new_otp)
        return True

    async def verify_otp(self, token, auth_id, otp_type) -> OTP:
        _, otp_query = self.get_by_auth_id(auth_id)
        if otp_query is None or otp_query.otp != token:
            return None
        if otp_query.otp_type != otp_type:
            raise InvalidRequest("Invalid Otp Type")
        return otp_query


crud_otp = CRUDOtp(db=get_db(), model=OTP)


def get_crud_otp(db=Depends(get_db)):
    return CRUDOtp(db=db, model=OTP)
