from typing import List, Union
from fastapi import Depends
import sqlalchemy
import sqlalchemy.orm

from core.db import get_db
from crud.base import CRUDBase
from models import Order, OrderItem, ShippingDetails, PaymentDetails
from schemas import (
    CheckoutCreate,
    PaymentDetailsCreate,
    OrderItemsCreate,
    ShippingDetailsCreate,
)


class CRUDOrder(CRUDBase[Order, CheckoutCreate, CheckoutCreate]):

    async def get_all_orders(self) -> List[Order]:
        query = (
            self._db.query(self.model)
            .options(
                sqlalchemy.orm.joinedload(Order.order_items),
                sqlalchemy.orm.joinedload(Order.payment_details),
                sqlalchemy.orm.joinedload(Order.shipping_details),
                sqlalchemy.orm.joinedload(Order.order_status),
            )
            .all()
        )
        return query

    async def delete_all_order(self):
        query = self._db.query(self.model).delete()


class CRUDOrderItem(CRUDBase[OrderItem, OrderItemsCreate, OrderItemsCreate]):
    def get_by_order_id(self, order_id: int) -> Union[List[OrderItem], None]:
        query = self._db.query(self.model).filter(self.model.order_id == order_id).all()
        return query if query else None


class CRUDShippingDetails(
    CRUDBase[ShippingDetails, ShippingDetailsCreate, ShippingDetailsCreate]
):
    pass


class CRUDPaymentDetails(
    CRUDBase[PaymentDetails, PaymentDetailsCreate, PaymentDetailsCreate]
):
    def get_by_payment_ref(self, payment_ref) -> Union[PaymentDetails, None]:
        query = (
            self._db.query(self.model)
            .filter(self.model.payment_ref == payment_ref)
            .first()
        )
        return query if query else None


crud_order = CRUDOrder(db=get_db(), model=Order)


def get_crud_order(db=Depends(get_db)) -> CRUDOrder:
    return CRUDOrder(db=db, model=Order)


def get_crud_order_item(db=Depends(get_db)) -> CRUDOrderItem:
    return CRUDOrderItem(db=db, model=OrderItem)


def get_crud_shipping_details(db=Depends(get_db)) -> CRUDShippingDetails:
    return CRUDShippingDetails(db=db, model=ShippingDetails)


def get_crud_payment_details(db=Depends(get_db)) -> CRUDPaymentDetails:
    return CRUDPaymentDetails(db=db, model=PaymentDetails)
