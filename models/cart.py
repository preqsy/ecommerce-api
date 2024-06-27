from __future__ import annotations

from core.db import Base
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    TIMESTAMP,
    text,
)
from sqlalchemy.orm import relationship

from models.product import Product


class Cart(Base):
    __tablename__ = "cart"
    id = Column(Integer, primary_key=True, nullable=False)
    product_id = Column(
        ForeignKey(column="products.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    customer_id = Column(
        ForeignKey(column="customers.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    quantity = Column(Integer, nullable=False, default=1)
    created_timestamp = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_timestamp = Column(DateTime, nullable=True)

    customer = relationship("Customer", back_populates="cart_items")
    product = relationship(Product, back_populates="cart_items")
