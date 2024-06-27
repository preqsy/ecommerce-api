from fastapi import Depends
import sqlalchemy
import sqlalchemy.orm

from core.db import get_db
from crud.base import CRUDBase
from models import Order, OrderStatus, OrderItem, ShippingDetails, PaymentDetails
from schemas import (
    OrderCreate,
    PaymentDetailsCreate,
    OrderItemsCreate,
    ShippingDetailsCreate,
    OrderStatusCreate,
)


class CRUDOrder(CRUDBase[Order, OrderCreate, OrderCreate]):

    async def get_all_orders(self):
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


class CRUDOrderStatus(CRUDBase[OrderStatus, OrderStatusCreate, OrderStatusCreate]):
    pass


class CRUDOrderItem(CRUDBase[OrderItem, OrderItemsCreate, OrderItemsCreate]):
    pass


class CRUDShippingDetails(
    CRUDBase[ShippingDetails, ShippingDetailsCreate, ShippingDetailsCreate]
):
    pass


class CRUDPaymentDetails(
    CRUDBase[PaymentDetails, PaymentDetailsCreate, PaymentDetailsCreate]
):
    pass


crud_order = CRUDOrder(db=get_db(), model=Order)


def get_crud_order(db=Depends(get_db)) -> CRUDOrder:
    return CRUDOrder(db=db, model=Order)


def get_crud_order_status(db=Depends(get_db)) -> CRUDOrderStatus:
    return CRUDOrderStatus(db=db, model=OrderStatus)


def get_crud_order_item(db=Depends(get_db)) -> CRUDOrderItem:
    return CRUDOrderItem(db=db, model=OrderItem)


def get_crud_shipping_details(db=Depends(get_db)) -> CRUDShippingDetails:
    return CRUDShippingDetails(db=db, model=ShippingDetails)


def get_crud_payment_details(db=Depends(get_db)) -> CRUDPaymentDetails:
    return CRUDPaymentDetails(db=db, model=PaymentDetails)
