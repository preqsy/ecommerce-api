from datetime import datetime, timedelta
from typing import List, Optional
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


class CRUDOrderItem(CRUDBase[OrderItem, OrderItemsCreate, OrderItemsCreate]):

    def get_by_order_id(self, order_id: int) -> Optional[List[OrderItem]]:
        query = self._db.query(self.model).filter(self.model.order_id == order_id).all()
        return query if query else None

    async def get_order_items_by_vendor_id(
        self, vendor_id
    ) -> Optional[List[OrderItem]]:
        query = (
            self._db.query(self.model).filter(self.model.vendor_id == vendor_id).all()
        )
        return query if query else None

    async def get_order_items_by_vendor_id_and_date(
        self, vendor_id, days: int = 30, limit: int = 20, skip: int = 0
    ) -> Optional[List[OrderItem]]:
        query_date = datetime.utcnow() - timedelta(days=days)

        query = (
            self._db.query(self.model)
            .filter(self.model.vendor_id == vendor_id)
            .filter(self.model.created_timestamp >= query_date)
            .limit(limit)
            .offset(skip)
            .all()
        )
        return query if query else None


class CRUDShippingDetails(
    CRUDBase[ShippingDetails, ShippingDetailsCreate, ShippingDetailsCreate]
):
    pass


class CRUDPaymentDetails(
    CRUDBase[PaymentDetails, PaymentDetailsCreate, PaymentDetailsCreate]
):

    def get_by_payment_ref(self, payment_ref) -> Optional[PaymentDetails]:
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
