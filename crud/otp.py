from fastapi import Depends
from core.db import get_db
from crud.base import CRUDBase
from models.auth_user import OTP
from schemas.otp import OTPCreate
from utils.generate_otp import generate_otp
from sqlalchemy import desc


class CRUDOtp(CRUDBase[OTP, OTPCreate, OTPCreate]):

    def create(self, auth_user_id: int) -> bool:
        otp_data = generate_otp()
        new_otp = OTP(auth_id=auth_user_id, otp=otp_data)
        self._db.add(new_otp)
        self._db.commit()
        self._db.refresh(new_otp)
        return True

    async def verify_otp(self, token, auth_id):
        _, otp_query = self.get_by_auth_id(auth_id)
        if otp_query is None or otp_query.otp != token:
            return None
        return otp_query


crud_otp = CRUDOtp(db=get_db(), model=OTP)


def get_crud_otp(db=Depends(get_db)):
    return CRUDOtp(db=db, model=OTP)
