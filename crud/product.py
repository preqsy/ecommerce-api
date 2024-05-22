from typing import List, Union
from fastapi import Depends
from sqlalchemy import desc

from core.db import get_db
from crud.base import CRUDBase
from models.cart import Cart
from models.product import Product
from schemas import ProductCreate
from schemas.product import CartCreate, ProductUpdate


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


class CRUDCart(CRUDBase[Cart, CartCreate, CartCreate]):
    def get_cart_items(self, customer_id) -> Union[List, None]:
        cart_details = (
            self._db.query(self.model)
            .filter(self.model.customer_id == customer_id)
            .all()
        )
        if not cart_details:
            return None
        return cart_details

    async def delete_cart(self, id) -> bool:
        cart_query = self._db.query(self.model).filter(self.model.customer_id == id)
        cart_query.delete(synchronize_session=False)
        self._db.commit()
        return


def get_crud_product(db=Depends(get_db)) -> CRUDProduct:
    return CRUDProduct(db=db, model=Product)


def get_crud_cart(db=Depends(get_db)) -> CRUDCart:
    return CRUDCart(db=db, model=Cart)
