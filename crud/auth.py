from typing import Type
from fastapi import Depends
from pydantic import EmailStr
from sqlalchemy.orm import Session
from core.db import get_db
from crud.base import CRUDBase
from models.auth_user import AuthUser
from schemas import AuthUserCreate


class CRUDAuthUser(CRUDBase[AuthUser, AuthUserCreate, AuthUserCreate]):
    def get_by_email(self, email: EmailStr) -> AuthUser:
        email_query = (
            self._db.query(self.model).filter(self.model.email == email).first()
        )
        if not email_query:
            return None
        return email_query

    async def update_email_or_phone_status(self, id, data_dict: dict) -> bool:
        user_query = self._db.query(self.model).filter(self.model.id == id)
        if not user_query:
            return None
        user_query.update(data_dict, synchronize_session=False)
        self._db.commit()

        return

    async def update_password(self, data_dict: dict, id: int):
        user_query = self._get_query_by_id(id)
        user_query.update(data_dict, synchronize_session=False)
        return


crud_auth_user = CRUDAuthUser(db=get_db(), model=AuthUser)


def get_crud_auth_user(db=Depends(get_db)):
    return CRUDAuthUser(db=db, model=AuthUser)
