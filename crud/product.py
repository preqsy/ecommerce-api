from typing import List, Union
from fastapi import Depends
from sqlalchemy import desc

from core.db import get_db
from crud.base import CRUDBase
from models import Product, ProductCategory, ProductImage, Order
from schemas import ProductCreate
from schemas import OrderCreate, ProductUpdate
from schemas.product import ProductCategoryCreate, ProductImageCreate


class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):

    def get_products(
        self, search: str | None, skip=0, limit=10
    ) -> Union[List[Product], None]:

        product_query = (
            self._db.query(self.model)
            .filter(self.model.product_name.ilike(f"%{search}%"))
            .filter(self.model.product_status == True)
            .order_by(desc(self.model.created_timestamp))
            .offset(skip)
            .limit(limit)
        ).all()

        return product_query if product_query else None

    def get_products_for_vendor(
        self, vendor_id: int, search: str | None, skip=0, limit=10
    ) -> Union[List[Product], None]:

        product_query = (
            self._db.query(self.model)
            .filter(self.model.vendor_id == vendor_id)
            .filter(self.model.product_name.ilike(f"%{search}%"))
            .filter(self.model.product_status == True)
            .order_by(desc(self.model.created_timestamp))
            .offset(skip)
            .limit(limit)
            .all()
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


class CRUDProductImage(CRUDBase[ProductImage, ProductImageCreate, ProductImageCreate]):
    pass


class CRUDProductCategory(
    CRUDBase[ProductCategory, ProductCategoryCreate, ProductCategoryCreate]
):
    def get_by_category_name(self, category_name):
        query = (
            self._db.query(self.model)
            .filter(self.model.category_name == category_name)
            .first()
        )
        return query if query else None


class CRUDOrder(CRUDBase[Order, OrderCreate, OrderCreate]):
    pass


crud_order = CRUDOrder(db=get_db(), model=Order)
crud_product_image = CRUDProductImage(db=get_db(), model=ProductImage)
crud_product_category = CRUDProductCategory(db=get_db(), model=ProductCategory)


def get_crud_order(db=Depends(get_db)) -> CRUDOrder:
    return CRUDOrder(db=db, model=Order)


def get_crud_product(db=Depends(get_db)) -> CRUDProduct:
    return CRUDProduct(db=db, model=Product)


def get_crud_product_image(db=Depends(get_db)) -> CRUDProductImage:
    return CRUDProductImage(db=db, model=ProductImage)


def get_crud_product_category(db=Depends(get_db)) -> CRUDProductCategory:
    return CRUDProductCategory(db=db, model=ProductCategory)
