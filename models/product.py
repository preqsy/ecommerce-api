from __future__ import annotations
from typing import ClassVar

from sqlalchemy.orm import relationship
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

from core.db import Base


class Product(Base):
    __tablename__ = "products"

    STOCK: ClassVar[str] = "stock"

    id = Column(Integer, primary_key=True, nullable=False)
    vendor_id = Column(
        ForeignKey("vendors.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    product_name = Column(String, nullable=False, index=True)
    short_description = Column(String(length=50), nullable=False)
    sku = Column(String, unique=True, nullable=False)
    product_status = Column(Boolean, nullable=False)
    long_description = Column(TEXT, nullable=True)
    stock = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    created_timestamp = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_timestamp = Column(DateTime, nullable=True)
    product_category_id = Column(
        ForeignKey("product_category.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )

    cart_items = relationship("Cart", back_populates="product")
    product_images = relationship(
        "ProductImage", back_populates="product", cascade="all, delete-orphan"
    )
    category = relationship("ProductCategory", back_populates="products")
    reviews = relationship("ProductReview")


class ProductCategory(Base):
    __tablename__ = "product_category"

    CATEGORY_NAME: ClassVar[str] = "category_name"
    id = Column(Integer, primary_key=True, nullable=False)
    category_name = Column(String, nullable=False, index=True)
    created_timestamp = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_timestamp = Column(DateTime, nullable=True)

    products = relationship(Product, back_populates="category")


class ProductImage(Base):
    __tablename__ = "product_image"

    id = Column(Integer, primary_key=True, nullable=False)
    product_image = Column(String, nullable=False)
    product_id = Column(
        ForeignKey("products.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    created_timestamp = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_timestamp = Column(DateTime, nullable=True)
    product = relationship(Product, back_populates="product_images")


class ProductReview(Base):
    __tablename__ = "product_reviews"

    id = Column(Integer, primary_key=True, nullable=False)
    product_id = Column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    review = Column(
        String(length=200),
        nullable=False,
    )
    rating = Column(Float, nullable=False)
    created_timestamp = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_timestamp = Column(DateTime, nullable=True)
