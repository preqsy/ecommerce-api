from __future__ import annotations

from core.db import Base
from sqlalchemy import (
    ARRAY,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    TIMESTAMP,
    Table,
    text,
)
from sqlalchemy.orm import relationship

from models.product import Product

order_vendor_association = Table(
    "order_vendor_association",
    Base.metadata,
    Column(
        "order_id",
        Integer,
        ForeignKey("orders.id", ondelete="CASCADE", onupdate="CASCADE"),
    ),
    Column(
        "vendor_id",
        Integer,
        ForeignKey("vendors.id", ondelete="CASCADE", onupdate="CASCADE"),
    ),
)


class Cart(Base):
    __tablename__ = "cart"
    id = Column(Integer, primary_key=True, nullable=False)
    product_id = Column(
        ForeignKey(column="products.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    customer_id = Column(
        ForeignKey(column="customers.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=True,
    )
    session_id = Column(String, nullable=True, index=True)
    quantity = Column(Integer, nullable=False, default=1)
    created_timestamp = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_timestamp = Column(DateTime, nullable=True)

    customer = relationship("Customer", back_populates="cart_items")
    product = relationship(Product, back_populates="cart_items")


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, nullable=False)

    customer_id = Column(
        ForeignKey(column="customers.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=True,
    )
    vendor_ids = Column(ARRAY(item_type=Integer), nullable=False)
    shipping_address = Column(String, nullable=False)
    payment_type = Column(String, nullable=False)
    contact_information = Column(String, nullable=False)
    additional_note = Column(String, nullable=True)
    total_amount = Column(Integer, nullable=False)
    status = Column(String, default="processing")
    created_timestamp = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_timestamp = Column(DateTime, nullable=True)
