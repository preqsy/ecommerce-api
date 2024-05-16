from fastapi import Depends
from core.db import get_db
from crud.base import CRUDBase
from models.auth_user import Customer
from schemas.customer import CustomerCreate


class CRUDCustomer(CRUDBase[Customer, CustomerCreate, CustomerCreate]):
    # def get_by_auth_id(self, auth_id) -> Customer:
    #     auth_query = (
    #         self._db.query(self.model).filter(self.model.auth_id == auth_id).first()
    #     )
    pass


def get_crud_customer(db=Depends(get_db)):
    return CRUDCustomer(db=db, model=Customer)
