from __future__ import annotations

from core.db import Base
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    TIMESTAMP,
    text,
)
from sqlalchemy.orm import relationship
from .customer import Customer


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, nullable=False)

    customer_id = Column(
        Integer,
        ForeignKey(column="customers.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=True,
    )
    total_amount = Column(Integer, nullable=False)
    status = Column(String, default="processing")
    order_date = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_timestamp = Column(TIMESTAMP(timezone=True), nullable=True)

    order_items = relationship("OrderItem", back_populates="order")
    payment_details = relationship(
        "PaymentDetails", back_populates="order", uselist=False
    )
    shipping_details = relationship("ShippingDetails", back_populates="order")
    customer = relationship(Customer)


class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, nullable=False)

    order_id = Column(
        Integer,
        ForeignKey("orders.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    vendor_id = Column(
        Integer,
        ForeignKey("vendors.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    status = Column(String, default="processing")
    price = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    created_timestamp = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_timestamp = Column(TIMESTAMP(timezone=True), nullable=True)

    order = relationship("Order", back_populates="order_items")


class PaymentDetails(Base):
    __tablename__ = "payment_details"
    id = Column(Integer, primary_key=True, nullable=False)
    order_id = Column(
        Integer,
        ForeignKey(column="orders.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        unique=True,
    )
    payment_method = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    status = Column(String, default="processing")
    payment_ref = Column(String, nullable=True, unique=True)
    paid_at = Column(TIMESTAMP(timezone=True))
    created_timestamp = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_timestamp = Column(TIMESTAMP(timezone=True), nullable=True)

    order = relationship("Order", back_populates="payment_details")


class ShippingDetails(Base):
    __tablename__ = "shipping_details"
    id = Column(Integer, primary_key=True, nullable=False)
    order_id = Column(
        Integer,
        ForeignKey(column="orders.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    contact_information = Column(String, nullable=False)
    additional_note = Column(String, nullable=True)
    address = Column(String, nullable=False)
    state = Column(String, nullable=False)
    country = Column(String, nullable=False)
    shipping_date = Column(TIMESTAMP(timezone=True))
    created_timestamp = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_timestamp = Column(TIMESTAMP(timezone=True), nullable=True)

    order = relationship("Order", back_populates="shipping_details")
