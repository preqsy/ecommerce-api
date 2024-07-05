from fastapi import Depends

from core.db import get_db
from crud.base import CRUDBase
from models import Customer
from schemas import CustomerCreate


class CRUDCustomer(CRUDBase[Customer, CustomerCreate, CustomerCreate]):
    pass


def get_crud_customer(db=Depends(get_db)):
    return CRUDCustomer(db=db, model=Customer)
