from typing import List, Union
from fastapi import Depends
from sqlalchemy import desc

from core.db import get_db
from core.errors import MissingResources
from crud.base import CRUDBase
from models.cart import Cart, Order
from models.product import Product
from schemas import ProductCreate
from schemas.product import CartCreate, OrderCreate, ProductUpdate


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

    async def get_cart_summary(
        self,
        customer_id: int,
    ):
        cart_items = self.get_cart_items(customer_id)
        if not cart_items:
            raise MissingResources("No items in cart")

        total_amount = sum(item.quantity * item.product.price for item in cart_items)
        total_items_quantity = sum(item.quantity for item in cart_items)

        summary = {
            "total_items_quantity": total_items_quantity,
            "total_amount": total_amount,
            "cart_items": cart_items,
        }

        return summary


class CRUDOrder(CRUDBase[Order, OrderCreate, OrderCreate]):
    pass


crud_order = CRUDOrder(db=get_db(), model=Order)


def get_crud_order(db=Depends(get_db)) -> CRUDOrder:
    return CRUDOrder(db=db, model=Order)


def get_crud_product(db=Depends(get_db)) -> CRUDProduct:
    return CRUDProduct(db=db, model=Product)


def get_crud_cart(db=Depends(get_db)) -> CRUDCart:
    return CRUDCart(db=db, model=Cart)
