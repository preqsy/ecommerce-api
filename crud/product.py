from fastapi import Depends
from sqlalchemy import desc

from core.db import get_db
from crud.base import CRUDBase
from models.product import Product
from schemas import ProductCreate


class CRUDProduct(CRUDBase[Product, ProductCreate, ProductCreate]):

    def get_products(self, search: str | None, skip=0, limit=10) -> list:

        product_query = (
            self._db.query(self.model)
            .filter(
                self.model.product_name.ilike(f"%{search}%")
                | self.model.category.ilike(f"%{search}%")
            )
            .filter(self.model.product_status == True)
            .order_by(desc(self.model.created_timestamp))
            .offset(skip)
            .limit(limit)
        )

        return product_query


def get_crud_product(db=Depends(get_db)) -> CRUDProduct:
    return CRUDProduct(db=db, model=Product)
