from typing import Type
from fastapi import Depends
from pydantic import EmailStr
from sqlalchemy.orm import Session
from core.db import get_db
from crud.base import CRUDBase
from models.auth_user import AuthUser
from schemas.auth import AuthUserCreate


class CRUDAuthUser(CRUDBase[AuthUser, AuthUserCreate, AuthUserCreate]):
    def get_by_email(self, email: EmailStr):
        email_query = (
            self._db.query(self.model).filter(self.model.email == email).first()
        )
        if not email_query:
            return None
        return email_query


def get_crud_auth_user(db=Depends(get_db)):
    return CRUDAuthUser(db=db, model=AuthUser)
