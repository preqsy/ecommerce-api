from __future__ import annotations

from core.db import Base
from sqlalchemy import (
    TEXT,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    TIMESTAMP,
    text,
    Float,
)
from sqlalchemy.orm import relationship

# from models.cart import Cart


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, nullable=False)
    vendor_id = Column(
        ForeignKey(column="vendors.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    product_name = Column(String, nullable=False, index=True)
    product_image = Column(String, nullable=False)
    category = Column(String, nullable=False)
    short_description = Column(String(length=50), nullable=False)
    sku = Column(String, unique=True, nullable=False)
    product_status = Column(Boolean, nullable=False)
    long_description = Column(TEXT, nullable=True)
    stock = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    created_timestamp = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_timestamp = Column(DateTime, nullable=True)

    cart_items = relationship("Cart", back_populates="product")
