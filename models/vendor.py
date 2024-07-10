from __future__ import annotations

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    TIMESTAMP,
    text,
)
from core.db import Base


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, nullable=False)
    auth_id: Column[int] = Column(
        ForeignKey(column="auth_details.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    username = Column(String, nullable=False, unique=True)
    phone_number = Column(String, nullable=True, unique=True)
    country = Column(String, nullable=False)
    state = Column(String, nullable=False)
    address = Column(String, nullable=False)
    bio = Column(String, nullable=False)
    profile_picture = Column(String, nullable=True)
    ratings = Column(Integer, nullable=True)
    created_timestamp = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_timestamp = Column(DateTime, nullable=True)


class VendorRating(Base):
    __tablename__ = "vendor_ratings"

    id = Column(Integer, primary_key=True, nullable=False)
    vendor_id: Column[int] = Column(
        ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False
    )
    rating = Column(
        Integer,
        nullable=False,
    )
    created_timestamp = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_timestamp = Column(DateTime, nullable=True)


class VendorOrders(Base):
    __tablename__ = "vendor_orders"

    id = Column(Integer, primary_key=True, nullable=False)
    order_item = Column(String, nullable=False)
    created_timestamp = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_timestamp = Column(DateTime, nullable=True)
