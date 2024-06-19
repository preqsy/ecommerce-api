from typing import List, Union
from fastapi import Depends
from sqlalchemy import desc

from core.db import get_db
from crud.base import CRUDBase
from models.cart import Order
from models.product import Product
from schemas import ProductCreate
from schemas import OrderCreate, ProductUpdate


class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):

    def get_products(
        self, search: str | None, skip=0, limit=10
    ) -> Union[List[Product], None]:

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

    def get_products_for_vendor(
        self, vendor_id: int, search: str | None, skip=0, limit=10
    ) -> Union[List[Product], None]:

        product_query = (
            self._db.query(self.model)
            .filter(self.model.vendor_id == vendor_id)
            .filter(
                self.model.product_name.ilike(f"%{search}%")
                | self.model.category.ilike(f"%{search}%")
            )
            .filter(self.model.product_status == True)
            .order_by(desc(self.model.created_timestamp))
            .offset(skip)
            .limit(limit)
        )
        if not product_query:
            return None

        return product_query

    def sort_product_by_price(self, skip: int = 0, limit: int = 20) -> List[Product]:
        product_query = (
            self._db.query(self.model)
            .order_by(desc(self.model.price))
            .offset(skip)
            .limit(limit)
            .all()
        )
        return product_query


class CRUDOrder(CRUDBase[Order, OrderCreate, OrderCreate]):
    pass


crud_order = CRUDOrder(db=get_db(), model=Order)


def get_crud_order(db=Depends(get_db)) -> CRUDOrder:
    return CRUDOrder(db=db, model=Order)


def get_crud_product(db=Depends(get_db)) -> CRUDProduct:
    return CRUDProduct(db=db, model=Product)
