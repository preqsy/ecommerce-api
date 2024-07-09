from typing import Optional
from fastapi import Depends
from pydantic import EmailStr

from core.db import get_db
from core.schema import RefreshTokenCreate
from crud.base import CRUDBase
from models import AuthUser, RefreshToken
from schemas import AuthUserCreate


class CRUDAuthUser(CRUDBase[AuthUser, AuthUserCreate, AuthUserCreate]):
    def get_by_email(self, email: EmailStr) -> Optional[AuthUser]:
        email_query = (
            self._db.query(self.model).filter(self.model.email == email).first()
        )
        return email_query if email_query else None


class CRUDRefreshToken(CRUDBase[RefreshToken, RefreshTokenCreate, RefreshTokenCreate]):
    pass


crud_refresh_token = CRUDRefreshToken(db=get_db(), model=RefreshToken)
crud_auth_user = CRUDAuthUser(db=get_db(), model=AuthUser)


def get_crud_auth_user(db=Depends(get_db)):
    return CRUDAuthUser(db=db, model=AuthUser)


def get_crud_refresh_token(db=Depends(get_db)):
    return CRUDRefreshToken(db=db, model=RefreshToken)
