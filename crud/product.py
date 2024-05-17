from fastapi import Depends
from core.db import get_db
from crud.base import CRUDBase
from models.product import Product
from schemas.product import ProductCreate


class CRUDProduct(CRUDBase[Product, ProductCreate, ProductCreate]):
    pass


def get_crud_product(db=Depends(get_db)) -> CRUDProduct:
    return CRUDProduct(db=db, model=Product)
