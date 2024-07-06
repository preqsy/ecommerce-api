from typing import List, Union
from fastapi import Depends
from sqlalchemy import desc

import sqlalchemy
import sqlalchemy.orm

from core.db import get_db
from core.errors import MissingResources
from crud.base import CRUDBase
from models import Product, ProductCategory, ProductImage, ProductReview
from schemas import (
    ProductCreate,
    ProductUpdate,
    ProductCategoryCreate,
    ProductImageCreate,
    ProductReviewCreate,
    ProductReviewUpdate,
)


class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):

    def get_all_products(
        self, search: str | None, skip=0, limit=10
    ) -> Union[List[Product], None]:

        product_query = (
            self._db.query(self.model)
            .filter(self.model.product_name.ilike(f"%{search}%"))
            .filter(self.model.product_status == True)
            .order_by(desc(self.model.created_timestamp))
            .offset(skip)
            .limit(limit)
            .options(sqlalchemy.orm.joinedload(self.model.reviews))
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

        return product_query if product_query else None

    def sort_product_by_price(self, skip: int = 0, limit: int = 20) -> List[Product]:
        product_query = (
            self._db.query(self.model)
            .order_by(desc(self.model.price))
            .offset(skip)
            .limit(limit)
            .all()
        )
        return product_query

    def get_or_raise_exception(self, id: int) -> Product:
        query_result = self._db.query(self.model).filter(self.model.id == id).first()
        if not query_result or not query_result.product_status:
            raise MissingResources
        return query_result


class CRUDProductReview(
    CRUDBase[ProductReview, ProductReviewCreate, ProductReviewUpdate]
):
    pass


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


crud_product_image = CRUDProductImage(db=get_db(), model=ProductImage)
crud_product_category = CRUDProductCategory(db=get_db(), model=ProductCategory)


def get_crud_product(db=Depends(get_db)) -> CRUDProduct:
    return CRUDProduct(db=db, model=Product)


def get_crud_product_image(db=Depends(get_db)) -> CRUDProductImage:
    return CRUDProductImage(db=db, model=ProductImage)


def get_crud_product_category(db=Depends(get_db)) -> CRUDProductCategory:
    return CRUDProductCategory(db=db, model=ProductCategory)


def get_crud_product_review(db=Depends(get_db)) -> CRUDProductReview:
    return CRUDProductReview(db=db, model=ProductReview)
